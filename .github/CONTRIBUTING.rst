============
Contributing
============

Contributions are welcome, and are greatly appreciated! Every little bit helps, and credit will be given. While at its core Tabbycat is a software project, there is much more you can do than code. We encourage you to help translate the project and to help others on our Facebook group. Of course, we also welcome and appreciate all feedback, suggestions, and ideas for how to improve the wording, translation, and design of our interface and documentation.

Feel free to `join our Facebook group <https://www.facebook.com/groups/tabbycat.debate/>`_ if you have any questions about how to get started.

Feedback and ideas
==================

These can be added as issues in the `GitHub repository <https://github.com/TabbycatDebate/tabbycat/issues>`_; posts in our `Facebook group <https://www.facebook.com/groups/tabbycat.debate/>`_; or as an :ref:`email to the developers <authors>`.

Bug reports
===========

Please report bugs by opening a new issue in our `GitHub repository <https://github.com/TabbycatDebate/tabbycat/issues>`_. It is most helpful if you can include:

- How Tabbycat was installed (on Heroku, locally on macOS, `etc.`)
- Any details about your tournament and setup that might be helpful in troubleshooting
- Detailed steps for how to reproduce the bug

Translation
===========

We use `Crowdin <https://crowdin.com/project/tabbycat>`_ to manage the translations of the application as well as the documentation. We welcome contributions to existing languages and also to start new language translations. The application messages should be prioritized before the documentation. Contact :ref:`the developers <authors>` for access to the platform.

Development
===========

- To easily test your changes to Tabbycat you probably want a working :ref:`local install <install-local>` (without using Docker)
- Please submit pull requests for features and bug fixes against `develop` (but not `master`).
- We broadly use the `git-flow workflow <http://danielkummer.github.io/git-flow-cheatsheet/>`_.
- We use Django's testing tools — adding unit tests to new features is greatly appreciated

  - A number of our tests use `Selenium <http://selenium-python.readthedocs.io>`_ and `ChromeDriver <https://sites.google.com/a/chromium.org/chromedriver/>`_ to simulate in-browser functionality. They will fail if you do not have the Chrome browser and ChromeDriver installed.

- A number of extra dependencies are required for running tests, linting, and serving the documentation. These can be installed with::

    $ pip install -r 'config/requirements_development.txt'

- We use `pre-commit <https://pre-commit.com/>`_ to run code style checks (linters). To have them run as a git hook automatically before every commit::

    $ pre-commit install

- Our ``package.json`` provides a convenience command that runs a standard set of development tools simultaneously, such as the Django server and the automatic recompilation with live injecting of javascript and CSS. Once you have set ``USE_WEBPACK_SERVER=True`` in your ``settings_local.py`` you can then run this with::

    $ npm run serve

Generating test data
--------------------

There are management commands to help developers quickly generate data for use in testing, including results and feedback. A list of all commands can be found from ``dj help``, but the most useful in this context are:

- ``dj importtournament ( minimal8team | australs24team | bp88team )``, which imports participant data for the 8-team (``minimal8team``), 24-team Australs (``australs24team``) and 88-team BP (``bp88team``) demonstration tournaments respectively.
- ``dj simulaterounds ROUND [ROUND ROUND ...]``, which simulates all of the rounds specified, generating a draw, an adjudicator allocation and a complete set of random results (but not feedback).
- ``dj generatefeedback ROUND [ROUND ROUND ...]``, which randomly generates feedback for all existing debates in the specified rounds.
- ``dj generateresults ROUND [ROUND ROUND ...]``, which randomly generates results for all existing debates in the specified rounds. (You don't need to run this if you ran ``simulaterounds``, because that already does it.)

Rounds can be specified by sequence number (``seq``) or abbreviation. You can find more information about each of them by adding ``--help`` after the command name.

Database schema changes
-----------------------

When adding new features, it may be necessary to modify the database schema to support these new additions. After the changes are made, the migration files made by ``python manage.py makemigrations`` must also be committed. The migration files should also contain methods fill the new fields based on existing data if possible.

Fixture files (found under ``data/fixtures/``) may also need to be updated, which can be done by running the ``migrate_fixtures.py`` script under a unmigrated database, then committing the result.
::

    $ python data/migrate_fixtures.py develop (your branch)

Style guide
-----------

For the front end interface design there is a style guide available at "/style/" once a tournament has been setup.

For python code, we use `flake8 <http://flake8.readthedocs.io>`_ to check for a non-strict series of style rules. Warnings will trigger a CI build to fail. The entire codebase can be checked by using::

    $ pre-commit run flake8 --all-files

For stylesheets, we use `stylelint <https://stylelint.io>`_. The relevant code can be checked by using::

    $ npm run lint-sass

For javascript, we use `eslint <http://eslint.org/>`_ to enforce the `standardJS <https://standardjs.com>`_ style and the standard recommendation of the vue plugin for eslint. The relevant code can be checked by using::

    $ npm run lint-vue

Project organization
====================

Versioning convention
---------------------

Our convention is to increment the minor version whenever we add new functionality, and to increment the major version whenever:

- the database can't be migrated forwards using ``python manage.py migrate --no-input``, or
- there is a major change to how the tournament workflow goes, or
- we make some other change that is, in our opinion, significant enough to warrant a milestone.

We write `data migrations <https://docs.djangoproject.com/en/1.10/topics/migrations/#data-migrations>`_ to allow existing systems to be upgraded easily. However, we don't always support backward database migrations. Our expectation is that long-lived installations keep up with our latest version.

One day, we hope to have a public API in place to facilitate the integration with other debating tournament software, like registration or adjudicator feedback systems. If and when that happens, we'll probably revise this convention to be more in line with `Semantic Versioning <http://semver.org/>`_.

Starting from version 0.7.0, we use cat breeds as the code names for major versions.

Documentation
-------------

Documentation is created using `Sphinx <http://sphinx-doc.org/>`_ and hosted at `Read The Docs <https://readthedocs.org>`_. Pushes to ``develop`` will update the *latest* documentation set, while pushes to ``master`` will update the *stable* documentation set.

To preview the documentation locally, install the development dependencies and then  start the server::

    $ sphinx-autobuild docs docs/_build/html --port 7999

You should then be able to preview the docs at `127.0.0.1:7999 <http://127.0.0.1:7999>`_.

Project structure
-----------------

- ``bin`` contains a number of convenience scripts for starting/stopping Docker, and the webserver/asset pipeline.
- ``data`` contains the sample data sets and fixtures used to setup demo tournaments and in automated tests respectively
- ``docs`` contains our document source files and images (although some are linked from the root directory)
- ``tabbycat`` is the main directory containing the Django project
    - ``locale`` contains translation strings for shared templates (others are in respective app directories)
    - ``templates`` contains shared html templates, stylesheets, javascript source files, and Vue.js components/mixins.
    - ``utils`` contains shared utilities
    - All other folders are the Django apps that contain specific views, models, and templates for functions such as ``draw`` generation/display, or recording ``results``. Each has sub-folders for tests and templates.
- In the root directory there are a number of files defining our python and javascript dependencies, core configuration files, and key documents like the ``README``

Internationalization/Localization
---------------------------------

The `gettext <https://docs.djangoproject.com/en/2.2/topics/i18n/translation/>`_ framework is used to enable the translation of strings in Python files and Django templates. Backend in this context signifies these types of files.

The backend's translation files can be updated from the ``tabbycat`` directory using one or more of the supporting language codes (see settings.py)::

    $ dj makemessages -l es

To do more than one language, just specify ``-l`` multiple times, _e.g._ ``-les -lar``.

These can then be compiled using::

    $ dj compilemessages -l es

As it stands Heroku needs the .mo files pre-compiled (see `issue in Heroku Python buildpack <https://github.com/heroku/heroku-buildpack-python/issues/198>`_, so these are committed to Git. Note that the English (``en``) language files should not be compiled; their sole purpose is to provide a source language for `Crowdin <https://crowdin.com/project/tabbycat>`_.

Strings defined in Vue files must similarily be marked with ``gettext`` but must be added manually to ``tabbycat/locale/LANGUAGE_CODE/djangojs.po``, for each language supported. These can then compiled to javascript bundles using::

    $ dj compilemessages -l es        # or whichever language(s) you want to update
    $ dj compilejsi18n -l es

These are then also committed to git to save users needing to run `compilejsi18n` during setup. The resulting files are then bundled as part of the npm build task. Updating these translations in development (live-reload) requires the use of the ``cp-i18n`` npm task.

Release checklist
-----------------

1. Check that all migrations have been generated and committed into Git
2. Merge translations from the Crowdin pull request and compile messages
3. Bump version number in ``docs/conf.py`` and ``docs/api-schema.yml`` (if applicable)
4. Bump version number and (if applicable) codename in ``tabbycat/settings/core.py``
5. Update the main ``CHANGELOG.rst`` file (including release date)
6. Check the major current deployment options, including:
    1. The ``deploy_heroku.py`` script
    2. The Tabbykitten version
    3. Docker (macOS, Windows 10*) and Docker Toolbox (Windows 10 Home) methods
    4. Using Bash and Powershell on Windows
    5. Using Terminal on macOS (at least test out a fresh install of the npm/pip  dependencies)
7. Check that the last Github Actions build passed and run the full local test suite (this will include the Selenium tests that are not on Travis)
8. Shift remaining issues from the Github Milestone
9. Create and finish the release branch as per git-flow
10. Ensure the tag is correct (``vX.Y.Z``) and published to GitHub
11. Back-merge ``master`` to the ``kitten`` branch
12. Back-merge ``develop`` to the in-progress feature branches
13. Issue a formal release with change notes on GitHub
14. Post change notes on the Facebook page/group
