# Documentation

Documentation is created using [MkDocs](http://mkdocs.readthedocs.org/en/stable/) and hosted using [Read the Docs](https://readthedocs.org).

## Previewing Locally

Install Mkdocs:

    $ pip install mkdocs

Change into the docs directory:

    $ cd docs

Start the MkDocs server:

    $ mkdocs serve

Open the local site at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Style Guide

- Note that the page layouts/structures are set in ```mkdocs.yml```
- All pages should have their title at the top as an ```h1```
- All subheadings should be ```h2```s
- No inline html
- Prefer \# over \= for headings; \- over \* for lists; \* for emphasis and \__ for bold
- Note that any subheadings inside a file will show in the sidebar as a third level of navigation. Best use them sparingly, with lists or bolds taking the place of minor section seperators
- Asides, warnings, and notes should be formatted as such (a blockquote wrapped in italics with the type of the concern bolded:
    ```
    > *___Note:__ This is the content of a note*
    ```
- Images should be placed in an /images folder within the relevant section