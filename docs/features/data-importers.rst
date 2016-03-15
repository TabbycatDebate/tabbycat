.. _tournament-data-importers:

=========================
Tournament Data Importers
=========================

This page describes how to write your own tournament data importer. It is aimed at an audience that is familiar with programming in Python, and may be willing to get their head around the Django model if necessary.

The **tournament data importer** is the class that imports data from one or more files (usually CSV files) into the database. A base class ``BaseTournamentDataImporter`` is in `importer/base.py <https://github.com/czlee/tabbycat/blob/develop/importer/base.py>`_. An example of a data importer is in `importer/anorak.py <https://github.com/czlee/tabbycat/blob/develop/importer/anorak.py>`_.

Why write your own?
===================

While Tabbycat has standard import formats, you might find that none of them fit the data that you need to import.

It's not possible to devise a single, universally-convenient import file format. Tabbycat supports way too many permutations of configurations for this to be workable. Instead, we provide the ones that have been useful before and are therefore likely to be useful again—but if your tournament has different needs, you might decide that it's easier to write an importer to conform to you, rather than conform to the importer.

Basic workflow
==============

1. Choose a name. We name importers after items of clothing in alphabetical order (starting at 'Anorak').
2. Write a subclass of ``BaseTournamentDataImporter``.
3. Write the front-end interface. This will probably be a `Django management command <https://docs.djangoproject.com/en/1.9/howto/custom-management-commands/>`_.

.. todo:: This page is incomplete. If you'd like to write your own tournament data importer, please contact Chuan-Zheng using the contact details in the :ref:`authors` section.
 
