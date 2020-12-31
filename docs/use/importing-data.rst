.. _importing-initial-data:

======================
Importing Initial Data
======================

Once you've got Tabbycat installed, the next step is to import data for the tournament: that is, import details of teams, speakers, adjudicators and rounds. There are a few ways to do this, each with their advantages and disadvantages.

To help you decide which to choose, here's a summary:

+----------------------+-------------------+--------------------+----------------------+
|        Method        |      Best for     |      Drawcard      |       Drawback       |
+======================+===================+====================+======================+
| **Demonstration      | Trying out        | Loads sample data  | Not for use with     |
| data**               | Tabbycat          | in one click       | real tournaments     |
|                      |                   |                    |                      |
+----------------------+-------------------+--------------------+----------------------+
| **Simple             | Small and         | Easy to use        | Only deals with      |
| importer**           | medium-sized      |                    | basic data           |
|                      | tournaments       |                    |                      |
+----------------------+-------------------+--------------------+----------------------+
| **Edit               | Adding data not   | Can handle all     | Adding large amounts |
| database**           | handled by the    | types of           | of data is time      |
|                      | simple importer   | information        | consuming            |
|                      | or editing        |                    |                      |
|                      | existing data     |                    |                      |
+----------------------+-------------------+--------------------+----------------------+
| **API**              | Tournaments with  | Less manual        | Requires programming |
|                      | external          | intervention       | knowledge or use of  |
|                      | registration      |                    | an existing external |
|                      | systems           |                    | application          |
+----------------------+-------------------+--------------------+----------------------+
| **Developing your    | Large tournaments | Easier to repeat,  | Requires a           |
| own importer**       | with custom needs | will take          | programming          |
|                      |                   | information in     | background and       |
|                      |                   | whatever format it | learning about the   |
|                      |                   | is already in      | API schema           |
+----------------------+-------------------+--------------------+----------------------+

Demonstration data
==================
If you're just learning or experimenting with Tabbycat, there are two demonstration datasets available, each with a sample set of teams, adjudicators, *etc.*, so that you can immediately start running rounds. Just be aware that these probably won't relate to anyone at your real-life tournament.

To load a demonstration dataset, click **New Tournament** link on the home page (once logged in as admin). You'll see a page titled "Create New Tournament". Scroll to the bottom of this page and click on one of the links at the bottom.

Simple importer
===============
The simple importer is the easiest way to get a tournament going, and we recommend it for small- and medium-sized tournaments. It allows you to add institutions, teams, adjudicators, venues, venue categories and venue constraints. (If you need to add anything else, use the :ref:`Edit Database area <import-edit-database>` instead.)

To get started, create a new tournament using the **New Tournament** link on the home page (once logged in as admin). It'll ask you for a few basic pieces of information.

.. image:: images/create-tournament.png

Then, once you're in your tournament, click **Setup** in the left-hand menu, then **Import Data**, to open the simple importer.

.. image:: images/simple-importer.png

You first need to add institutions. Once institutions are added, you can then add teams and adjudicators in the relevant sections. Each of these is a two-step process:

- For **institutions** and **venues**, it will first ask you to copy-paste a list of names and properties in a comma-separated table format.  The second step is to confirm individual fiels.
- For **teams** and **adjudicators**, it will first ask you how many teams/adjudicators to add for each institution (or who lack an institutional affiliation). The second step is to fill in their details, for example, names.

.. image:: images/add-institutions.png

.. image:: images/add-teams-1.png

.. image:: images/add-teams-2.png

Finally, if you would like to use venue categories and/or :ref:`venue constraints <venue-constraints>`, you can do so using the two last sections of the simple importer.

.. note:: If copying and pasting from a spreadsheet, an easy way to make a comma-separated table is to save a spreadsheet with the relevant information as a \*.csv file, then open this file in a plain text editor (such as Notepad or TextEdit), and copying it from there.

.. _import-edit-database:

Editing the database
====================
Sometimes, the simple importer just isn't enough---whether because you need more customization than the simple importer handles (*e.g.* adjudicator feedback questions), or because some participants changed their details after you imported the inital data. In this case, the easiest thing to do is to edit the database via the Django administrative interface (under Setup > Edit Database).

The general pattern goes like this: Go to **Setup > Edit Database**, find the type of object you wish to add/change, and click "Add" or "Change". Then, fill in what you need to and save the object.

.. caution:: The Edit Database area is very powerful, and naturally if you mess things up, you can insert potentially catastrophic inconsistencies into the database. For participant information this is hard to do, but it's worth keeping in mind.

Application Programming Interface (API)
=======================================

Participants can be imported in Tabbycat through the :ref:`API <api>`, using authenticated endpoints making ``POST`` requests to the relevant endpoints, as described in the ``api-schema.yml`` file. There are also many existing tools to import data from various filetypes and external systems, or you can create your own.
