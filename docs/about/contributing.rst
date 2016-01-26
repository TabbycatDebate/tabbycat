.. _contributing:

============
Contributing
============

.. important:: We are using the `git-flow workflow <http://danielkummer.github.io/git-flow-cheatsheet/>`_, so please submit any pull requests against the **develop branch** (and not master).

Contributions are welcome, and are greatly appreciated! Every little bit helps, and credit will be given. `Join our Facebook group <https://www.facebook.com/groups/tabbycat.debate/>`_.

How to contribute
=================

Bug reports
-----------

Please report bugs by opening a new issue in our `GitHub repository <https://github.com/czlee/tabbycat/issues>`_.

It is most helpful if you can include:

- How Tabbycat was installed (on Heroku, locally on OS X, `etc.`)
- Any details about your tournament and setup that might be helpful in troubleshooting
- Detailed steps for how to reproduce the bug

Bug fixes
---------

Look through the GitHub issues for bugs. Anything tagged with "bug" is open to whoever wants to implement it.

Feature requests
----------------

.. todo:: We haven't written this section yet.

Feature implementations
-----------------------

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Documentation
-------------

.. todo:: We haven't written this section yet.

Getting Started
===============

- Insert general setup instructions
- Insert instructions on how to make a feature/bug branch
- Maybe insert instructions on how to run tests / flake8
- Insert pull request checklist/guidelines

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

Install the docs-specific requirements (from the base folder):

  $ pip install -r 'docs/requirements.txt'

Start the server:

  $ sphinx-autobuild docs docs/_build/html --port 7999

You should then be able to preview the docs at `127.0.0.1:7999 <http://127.0.0.1:7999>`

Provisional Style Guide
-----------------------

- All pages should have their title at the top as an ``h1`` in
- Headings should use Title Case
- All subheadings should be ``h2``
- Note that any subheadings inside a file will show in the sidebar as a third level of navigation. Best use them sparingly, with lists or bolds taking the place of minor section seperators
- No inline html
- Prefer:
    - `#` over `=` for headings
    - `-` over `*` for lists
    - `*` for emphasis and `__` for bold
- Use `admonitions <http://docutils.sourceforge.net/docs/ref/rst/directives.html#admonitions>`_ for notes, cautions, warnings and so on.
- Images should be placed in an /images folder within the relevant section