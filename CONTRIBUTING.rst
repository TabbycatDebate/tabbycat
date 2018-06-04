============
Contributing
============

Contributions are welcome, and are greatly appreciated! Every little bit helps, and credit will be given. While at its core Tabbycat is a software project, you do not need to know how to code or use Git in order to help. We welcome feedback and ideas based on your tabbing experience and appreciate suggestions or proposals for how to improve the wording, translation, and design of our interface and documentation.

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

Getting started with development
================================

- To easily test your changes to Tabbycat you probably want a working :ref:`local install <install-local>` (without using Docker)
- Generally we prefer that features and bug fixes are submitted as pull requests on their own branch (as described in the  `git-flow workflow <http://danielkummer.github.io/git-flow-cheatsheet/>`_). Submitting against `develop` (but not `master`) is fine for small fixes and changes.
- We use Django's testing tools — it would be great if new features came with unit tests

    - A number of our tests use `Selenium <http://selenium-python.readthedocs.io>`_ and `ChromeDriver <https://sites.google.com/a/chromium.org/chromedriver/>`_ to simulate in-browser functionality. They will fail if you do not have the Chrome browser installed.

- By default the development server's build process will broadcast livereload events; installing one of their `browser plugins <http://livereload.com/extensions/>`_ can make testing front-end changes easier.
- A number of extra dependencies are required for running tests, linting, and serving the documentation. These can be installed with::

    $ pip install -r 'requirements_development.txt'

- The email backend should be changed in ``local_settings.py`` to display sent messages in ``STDOUT``, not by real email. Insert::

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

Style guide
===========

For python code, we use `flake8 <http://flake8.readthedocs.io>`_ to check for a non-strict series of style rules. Warnings will trigger a Travis CI build to fail. The entire codebase can be checked by using::

    $ flake8 .

For stylesheets, we use `stylelint <https://stylelint.io>`_ to enforce the `AirBnB CSS styleguide <https://github.com/airbnb/css>`_. The relevant code can be checked by using::

    $ npm run stylelint

For javascript, we use `eslint <http://eslint.org/>`_ to enforce the `AirBnB javascript  styleguide <https://github.com/airbnb/javascript>`_. The relevant code can be checked by using::

    $ npm run eslint

For the front end interface design there is a style guide available at "/style/" once a tournament has been setup.

Versioning convention
=====================

Our convention is to increment the minor version whenever we add new functionality, and to increment the major version whenever:

- the database can't be migrated forwards using ``python manage.py migrate --no-input``, or
- there is a major change to how the tournament workflow goes, or
- we make some other change that is, in our opinion, significant enough to warrant a milestone.

Most of the time, we write `data migrations <https://docs.djangoproject.com/en/1.10/topics/migrations/#data-migrations>`_ to allow existing systems to be upgraded easily. However, we don't always support backward database migrations. Our expectation is that long-lived installations keep up with our latest version.

One day, we hope to have a public API in place to facilitate the integration with other debating tournament software, like registration or adjudicator feedback systems. If and when that happens, we'll probably revise this convention to be more in line with `Semantic Versioning <http://semver.org/>`_.

Starting from version 0.7.0, we use cat breeds as the code names for major versions.

Documentation
=============

Documentation is created using `Sphinx <http://sphinx-doc.org/>`_ and hosted at `Read The Docs <https://readthedocs.org>`_. Pushes to ``develop`` will update the *latest* documentation set, while pushes to ``master`` will update the *stable* documentation set.

To preview the documentation locally, install the development dependencies and then  start the server::

    $ sphinx-autobuild docs docs/_build/html --port 7999

You should then be able to preview the docs at `127.0.0.1:7999 <http://127.0.0.1:7999>`_.

Project Structure
=================

- ``bin`` contains a number of convenience scripts for starting/stopping Docker, and the webserver/asset pipeline.
- ``data`` contains the sample data sets and fixtures used to setup demo tournaments and in automated tests respectively
- ``docs`` contains our document source files and images (although some are linked from the root directory)
- ``tabbycat`` is the main directory containing the Django project
    - ``locale`` contains translation strings for shared templates (others are in respective app directories)
    - ``templates`` contains shared html templates, stylesheets, javascript source files, and Vue.js components/mixins.
    - ``utils`` contains shared utilities
    - All other folders are the Django apps that contain specific views, models, and templates for functions such as ``draw`` generation/display, or recording ``results``. Each has sub-folders for tests and templates.
- In the root directory there are a number of files defining our python and javascript dependencies, core configuration files, and key documents like the ``README``

Translations
============

The backend's translation files can be updated from the ``tabbycat`` directory using one or more of the supporting language codes (see settings.py)::

    $ dj makemessages -l es

To do more than one language, just specify ``-l`` multiple times, _e.g._ ``-les -lar``.

These can then be compiled using::

    $ dj compilemessages -l es

As it stands Heroku needs the .mo files pre-compiled (see `issue in Heroku Python buildpack <https://github.com/heroku/heroku-buildpack-python/issues/198>`_, so these are committed to Git. Note that the English (``en``) language files should not be compiled; their sole purpose is to provide a source language for Transifex.

The frontend's translation files are manually updated in ``tabbycat/locale/LANGUAGE_CODE/djangojs.po``. These can then compiled to javascript bundles using::

    $ dj compilemessages -l es        # or whichever language(s) you want to update
    $ dj compilejsi18n -l es

These are then also committed to git to save users needing to run `compilejsi18n` during setup. The resulting files are then bundled as part of a gulp task.

Release Checklist
=================

1. Check that all migrations have been generated and committed into Git
2. Bump version number in ``docs/conf.py``
3. Bump version number and (if applicable) codename in ``tabbycat/settings.py``
4. Update the main ``CHANGELOG.rst`` file (including release date)
5. Check the major current deployment options, including:
    1. The ``deploy_heroku.py`` script
    2. The Tabbykitten version
    3. Docker (macOS, Windows 10*) and Docker Toolbox (Windows 10 Home) methods
    4. Using Bash and Powershell on Windows
    5. Using Terminal on macOS (at least test out a fresh install of the npm/pip  dependencies)
6. Check that the last Travis CI build passed and run the full local test suite (this will include the Selenium tests that are not on Travis)
7. Shift remaining issues from the Github Milestone
8. Create and finish the release branch as per git-flow
9. Ensure the tag is correct (``vX.Y.Z``) and published to GitHub
10. Back-merge ``master`` to the ``kitten`` branch
11. Back-merge ``develop`` to the in-progress feature branches
12. Issue a formal release with change notes on GitHub
13. Post change notes on the Facebook page/group
