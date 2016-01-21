from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth import get_user_model
from psycopg2 import IntegrityError

class Command(BaseCommand):

    help = "Post-deploy script for deploys from the 'Deploy to Heroku' button. " \
            "Not for use in local installations or deployments using the deploy_heroku.py script."

    def handle(self, **options):

        # Run migrations
        call_command('migrate')

        # Create a superuser with a default name and password
        User = get_user_model()
        if User.objects.filter(username='admin').exists():
            raise CommandError("The user 'admin' already exists.")
        User.objects.create_superuser('admin', '', 'admin')
