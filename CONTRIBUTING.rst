============
Contributing
============

.. important:: We are using the `git-flow workflow <http://danielkummer.github.io/git-flow-cheatsheet/>`_, so please submit any pull requests against the **develop branch** (and not master).

Contributions are welcome, and are greatly appreciated! Every little bit helps, and credit will be given. `Join our Facebook group <https://www.facebook.com/groups/tabbycat.debate/>`_.

Bug reports
===========

Please report bugs by opening a new issue in our `GitHub repository <https://github.com/czlee/tabbycat/issues>`_.

It is most helpful if you can include:

- How Tabbycat was installed (on Heroku, locally on OS X, `etc.`)
- Any details about your tournament and setup that might be helpful in troubleshooting
- Detailed steps for how to reproduce the bug

Getting started
===============

- Insert general setup instructions
- Insert instructions on how to make a feature/bug branch
- Maybe insert instructions on how to run tests
- Insert pull request checklist/guidelines

Style guide
===========

We use `flake8 <http://flake8.readthedocs.io>`_ to check for a non-strict series of style rules. Warnings will trigger a Travis CI build to fail. The entire codebase can be checked by using::

    $ flake8 .

While in the base directory

Semantic versioning convention
==============================

We follow `Semantic Versioning <http://semver.org/>`_. That said, since this is end-user software, there aren't any downstream dependencies so the concept of a "public API" isn't quite as obvious for Tabbycat as it is for projects more reliant on semantic versioning to manage dependencies. In complying with Semantic Versioning, we consider the following to be our "public API", along with the following criteria for backwards incompatibility:

 - **Database schema**
    - if it cannot be migrated forwards or backwards using the standard migration function without user-input defaults
    - if migration forwards would entail losing data or require reformatting data
 - **Management commands**
    - if a command that used to work no longer works
 - **GUI**
    - if there is a major change to the workflow of any user
 - **Tournament data importer, including tournament configuration**
    - if files that used to work would no longer work.
    - however, with tournament configuration, Tabbycat could in most cases detect deprecated settings and interpret them in any new framework with a warning message.

Starting from version 0.7.0, we use code names for versions, being breeds of cats in alphabetical order.

Documentation
=============

Documentation is created using `Sphinx <http://sphinx-doc.org/>`_ and hosted at `Read The Docs <https://readthedocs.org>`_. Pushes to ``develop`` will update the *latest* documentation set, while pushes to ``master`` will update the *stable* documentation set.

Previewing Locally
------------------

Install the docs-specific requirements (from the base folder)::

    $ pip install -r 'docs/requirements.txt'

Start the server::

    $ sphinx-autobuild docs docs/_build/html --port 7999

You should then be able to preview the docs at `127.0.0.1:7999 <http://127.0.0.1:7999>`
