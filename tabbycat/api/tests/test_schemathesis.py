import re
from contextlib import contextmanager
from urllib.parse import urlsplit

import schemathesis
from api.permissions import URLKeyAuthentication
from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIHandler
from django.core.signals import request_finished, request_started
from django.db import close_old_connections, transaction
from django.test import override_settings, tag
from django.urls import resolve
from hypothesis import given, HealthCheck, note, settings, strategies as st
from hypothesis.extra.django import TestCase
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from schemathesis.checks import not_a_server_error

from participants.models import Person
from tournaments.models import Tournament


@contextmanager
def keep_test_connection():
    signals = (request_started, request_finished)
    disconnected = [signal for signal in signals if signal.disconnect(close_old_connections)]
    try:
        yield
    finally:
        for signal in disconnected:
            signal.connect(close_old_connections)


@contextmanager
def isolated_scenario():
    cache.clear()
    with keep_test_connection(), transaction.atomic():
        yield
        transaction.set_rollback(True)


def path_pattern(template):
    return re.compile(re.sub(r'\\\{(\w+)\\\}', r'(?P<\1>[^/]+)', re.escape(template)))


def links(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, (dict, list)):
        for item in value.values() if isinstance(value, dict) else value:
            yield from links(item)


def linked_paths(value, patterns):
    for link in links(value):
        if not link.startswith(('/', 'http://', 'https://')):
            continue
        parsed = urlsplit(link)
        if parsed.hostname not in (None, 'localhost', 'testserver'):
            continue
        for template, pattern in patterns.items():
            match = pattern.fullmatch(parsed.path)
            if match is not None:
                yield template, match.groupdict(), parsed.path
                break


@tag('schemathesis')
@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'], STORAGES=django_settings.STORAGES | {
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class SchemaTests(TestCase):
    """Run request sequences against a tournament, restoring it between examples."""

    fixtures = ['after_round_4.json']

    def setUp(self):
        super().setUp()
        self.tournament = Tournament.objects.first()
        with keep_test_connection():
            self.schema = schemathesis.openapi.from_wsgi('/api/schema.yml', WSGIHandler())
        admin = get_user_model().objects.get(username='admin')
        self.token = Token.objects.get_or_create(user=admin)[0].key
        person = Person.objects.exclude(url_key__isnull=True).exclude(url_key='').first()
        self.participant_key = person.url_key
        self.client.raise_request_exception = False

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def authorization_for(self, path):
        view = resolve(re.sub(r'{[^}]+}', '1', path)).func.cls
        authenticators = view.authentication_classes
        if URLKeyAuthentication in authenticators and TokenAuthentication not in authenticators:
            return 'Key ' + self.participant_key
        return 'Token ' + self.token

    def resource_paths(self, fixture_paths, patterns):
        """Learn complete path bindings from links in the fixture's API responses."""
        paths = self.schema.raw_schema['paths']
        seeds = [template for template, methods in paths.items()
                 if 'get' in methods and set(re.findall(r'{([^}]+)}', template)) <= fixture_paths.keys()]
        queue = [template.format(**fixture_paths) for template in seeds]
        queued = set(seeds)
        bindings = {}

        for url in queue:
            with isolated_scenario():
                response = self.client.get(url, HTTP_AUTHORIZATION=self.authorization_for(url))
            self.assertLess(response.status_code, 500, url)
            if response.status_code != 200 or not response['Content-Type'].startswith('application/json'):
                continue
            for template, parameters, path in linked_paths(response.json(), patterns):
                bindings.setdefault(template, parameters)
                if 'get' in paths[template] and template not in queued:
                    queue.append(path)
                    queued.add(template)
        return bindings

    def test_operations(self):
        fixture_paths = {'tournament_slug': self.tournament.slug, 'round_seq': 1}
        paths = self.schema.raw_schema['paths']
        patterns = {template: path_pattern(template) for template in paths}
        initial_resources = self.resource_paths(fixture_paths, patterns)
        operations = [(path, method) for path, methods in paths.items()
                      for method in methods if method.upper() in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')]
        followups = {
            path: [(candidate, verb) for candidate, verb in operations
                   if candidate == path or candidate.startswith(path + '/')]
            for path, _ in operations
        }

        for first_path, first_method in operations:
            @settings(max_examples=3, deadline=None,
                      suppress_health_check=[HealthCheck.filter_too_much])
            @given(data=st.data())
            def check(data):
                resources = initial_resources.copy()
                path, method = first_path, first_method
                with isolated_scenario():
                    for step in range(3):
                        names = re.findall(r'{([^}]+)}', path)
                        defaults = {name: fixture_paths[name] for name in names if name in fixture_paths}
                        operation = self.schema[path][method.upper()]
                        case = data.draw(operation.as_strategy(),
                                         label=f'{step + 1}: {method.upper()} {path}')
                        case.path_parameters = (case.path_parameters or {}) | resources.get(path, defaults)
                        note(f'{method.upper()} {path}')
                        response = case.call_and_validate(
                            headers={'Authorization': self.authorization_for(path)},
                            checks=[not_a_server_error],
                        )
                        if response.status_code < 400:
                            try:
                                body = response.json()
                            except ValueError:
                                pass
                            else:
                                for template, parameters, _ in linked_paths(body, patterns):
                                    resources[template] = parameters
                        if step < 2:
                            path, method = data.draw(st.sampled_from(followups[path]),
                                                     label=f'operation {step + 2}')

            with self.subTest(path=first_path, method=first_method):
                check()
