# Contributing

**Important**: We are using the [git-flow workflow](http://danielkummer.github.io/git-flow-cheatsheet/), so please submit any pull requests against develop branch (and not master).

Contributions are welcome, and are greatly appreciated! Every little bit helps, and credit will be given.

## Options for Contributing

1. Report Bugs

    - Report bugs at [https://github.com/czlee/tabbycat/issues](https://github.com/czlee/tabbycat/issues).
    - If you are reporting a bug, please try to include include:
        - How Tabbycat was installed (on heroku, OS X, etc).
        - Any details about your tournament and setup that might be helpful in troubleshooting.
        - Detailed steps to reproduce the bug.

2. Fix Bugs

    - Look through the GitHub issues for bugs. Anything tagged with "bug" is open to whoever wants to implement it.

3. Request Features

    - Start an issue, tag as request. TODO: flesh out

4. Implement Features

    - Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

5. Write Documentation

    - TODO: flesh out

## Getting Started

- Insert general setup instructions
- Insert instructions on how to make a feature/bug branch
- Maybe insert instructions on how to run tests / flake8
- Insert pull request checklist/guidelines

## Versioning System

We follow [Semantic Versioning](http://semver.org/). That said, since this is end-user software, there aren't any downstream dependencies so the concept of a "public API" isn't quite as obvious for Tabbycat as it is for projects more reliant on semantic versioning to manage dependencies. In complying with Semantic Versioning, we consider the following to be our "public API", along with the following criteria for backwards incompatibility:

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

## Documentation System

Documentation is created using [MkDocs](http://mkdocs.readthedocs.org/en/stable/) and hosted using [Read the Docs](https://readthedocs.org). Pushes to ```develop``` will update the *latest* documentation set, while pushes to ```master``` will update the *stable* documentation set.

__Previewing Locally__

Install Mkdocs:

    $ pip install mkdocs

Change into the docs directory:

    $ cd docs

Start the MkDocs server:

    $ mkdocs serve -a localhost:9000

Open the local site at [http://127.0.0.1:9000/](http://127.0.0.1:9000/)

Page hierarchies and organisation are defined in ```mkdocs.yml```

__Provisional Style Guide__

- All pages should have their title at the top as an ```h1``` in
- Headings should use Title Case
- All subheadings should be ```h2```s
- Note that any subheadings inside a file will show in the sidebar as a third level of navigation. Best use them sparingly, with lists or bolds taking the place of minor section seperators
- No inline html
- Prefer:
    - `#` over `=` for headings
    - `-` over `*` for lists
    - `*` for emphasis and `__` for bold
- Asides, warnings, and notes should be formatted as such:
    - `> *___Note:__ This is the content of a note*`

    - > *___Note:__ This is the content of a note*
- Images should be placed in an /images folder within the relevant section
