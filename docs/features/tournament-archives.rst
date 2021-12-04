.. _tournament-archives:

===================
Tournament Archives
===================

What is it?
===========

Tabbycat provides a method to download data relating to a tournament, using XML. `XML <https://en.wikipedia.org/wiki/XML>`_, or Extensible Markup Language, is a file format used for the transfer of data between applications. This format attemps to provide all data in a way that is compatible with other tab systems and tools, and which can be re-imported into Tabbycat, reflecting changes made externally. As an archival format, this allows results of tournaments to be preserved through the publication in other mediums. Philip Belesky and Chuan-Zheng Lee have wrote an article, `*The Start of History* <https://github.com/TabbycatDebate/dta-spec/blob/master/The-Start-of-History.pdf>`_, detailing a proposal for such a format.

.. caution:: This should not be used in-place of :ref:`database backups <backups>`

Importing a Full Tournament
===========================

Tournament archive files have a standardized format and thus any tournament exported from an application supporting the format can be imported in Tabbycat. However, beware that there might not be feature parity between systems and thus some data may be lost.

A link to import a new tournament is available on the front page for admins. The file can then be uploaded. It can take a bit of time before everything is imported; you will be sent back to the front page during the importation.

Importing a Partial Tournament
==============================

The importer does not support importing only parts of a tournament, but rather the whole. This is as changes between the archive and the database may get lost and primary/foreign keys may not correspond. However, institutions with the same name as an existing institution in the database will not be touched, but used by the import.

Exporting a Tournament
======================

By default, all data relating to a tournament is exported. The page may take time to generate, especially for larger tournaments, but it will automatically download with the short name of the tournament as an XML file.

Schema
======

A schema for the format is available `on Github <https://github.com/TabbycatDebate/dta-spec>`_ for people wishing to implement the format in other tabulation systems or analyses.
