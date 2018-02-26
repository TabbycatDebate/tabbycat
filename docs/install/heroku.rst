.. _install-heroku:

====================
Installing on Heroku
====================

When running Tabbycat on the internet, we set it up on `Heroku <http://www.heroku.com/>`_. The project is set up to be good to go on Heroku, and it works well for us, so if you'd like to run it online, we recommend that you do the same. Naturally, this requires you to have a Heroku account.

There are two ways to do this: a **short way** and a **long way**. Most people should use the short way. The long way requires some familiarity with command-line interfaces and Git, and requires a :ref:`local installation <install-local>` as a prerequisite, but (unlike the short way) allows you to import data from CSV files.

The short way
=============
Click this button:

.. image:: https://www.herokucdn.com/deploy/button.svg
  :target: https://heroku.com/deploy?template=https://github.com/TabbycatDebate/tabbycat/tree/master

This is the easiest way to deploy an instance of Tabbycat online. It requires no technical background.

If you don't already have a Heroku account, it'll prompt you to create one. Once you're logged in to Heroku, choose a name for your installation, then scroll down and click **Deploy**. Once it's finished, click **View** and follow the prompts. Once finished, open the site and from there you can easily set up a demo data set (if you just want to learn Tabbycat) or use the data importer to set up a real tournament.

.. note:: During the setup process, Heroku will ask you to verify your account by adding a credit card. A standard Tabbycat site *will not charge* your card — charges only accrue if you deliberately add a paid service in the Heroku dashboard.

  If you can't access a credit card, you can instead install a limited version, which we call "Tabbykitten". However, Tabbykitten cannot send any e-mails, does not send error reports to the developers, and can handle much less public traffic. We therefore strongly recommend it only as a last resort, and even then only for small tournaments.  `Use this link to set up a Tabbykitten site <https://heroku.com/deploy?template=https://github.com/TabbycatDebate/tabbycat/tree/kitten>`_.

The long way
============
The long way sets you up with more control over your environment. Because you'll clone `our GitHub repository`_, it'll be easier for you to pull and contribute updates to the source code.  We recommend it if you have experience with Git.  It's also easier with this method to import CSV files using the command-line importer, so if you have a very large tournament, this might make importing initial data easier.

We've tested these instructions successfully on Windows, Linux and macOS.

Requisite technical background
------------------------------

You need to have at least a passing familiarity with command-line interfaces to get through the longer traditional method. We'll talk you through the rest.

When we say "command shell", on Windows we mean **Command Prompt**, and on Linux and macOS we mean **Terminal** (or your favourite command shell).

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a `Django <https://www.djangoproject.com/>`_ project. As such, it can be installed on any web platform that supports Django, using any SQL system that Django supports. Just be aware that we haven't tried any other platform.

Short version of the long way
-----------------------------
.. parsed-literal::

  git clone https\:\/\/github.com/TabbycatDebate/tabbycat.git
  git checkout |vrelease|                               # or master
  cd tabbycat
  python deploy_heroku.py <yourappname>

If you want to :ref:`import tournament data <importing-initial-data>` from CSV files, :ref:`install Tabbycat locally <install-local>`, put your CSV files in ``data/<yourtournamentname>``, then::

  createdb <yourlocaldatabasename>     # Your local_settings.py file must point here from DATABASES
  dj migrate
  dj createsuperuser
  dj importtournament <yourtournamentname> --name <Your Tournament Name> --short-name <Tournament>
  heroku maintenance:on
  heroku pg:reset
  heroku pg:push <yourlocaldatabasename> DATABASE
  heroku maintenance:off

1. Install dependencies
-----------------------

a. Install the `Heroku Command Line Interface (CLI) <https://devcenter.heroku.com/articles/heroku-cli>`_, then log in with the command ``heroku login``.

b. If you don't already have **Git**, follow the `instructions on the GitHub website <https://help.github.com/articles/set-up-git>`_ to set up Git.

2. Set up a local installation
------------------------------

If you don't already have a local installation, follow these instructions for your operating system to set up a local installation.

.. attention:: When downloading the source code, you **must** take the option involving cloning the GitHub repository using Git. In the macOS and Windows instructions, this means the option described in the "Advanced users" box. To do so, use these commands:

  .. parsed-literal::

      $ git clone https\:\/\/github.com/TabbycatDebate/tabbycat.git
      $ git checkout |vrelease|                              # or master

  Do not download the .tar.gz or .zip file and extract it.

- :ref:`install-linux`
- :ref:`install-osx`
- :ref:`install-wsl`
- :ref:`install-windows`

.. tip:: If you already have a local installation, you needn't go through the whole process again. However, you should run ``git pull`` to update to the latest version, then press ahead to step 3: Deploy to Heroku.

  It's not *strictly* necessary to have a fully functional local installation if you don't want to import data from CSV files. But it certainly helps.

3. Deploy to Heroku
-------------------

.. rst-class:: spaced-list

a. Navigate to your Tabbycat directory::

    cd path/to/my/tabbycat/directory

b. Run the script to deploy the app to Heroku. Replace ``<yourappname>`` with your preferred URL. Your website will be at ``<yourname>.herokuapp.com``.

  ::

    python deploy_heroku.py <yourappname>

  This script has other options that you might find useful. Run ``python deploy_heroku.py --help`` for details.

  When this script finishes, it will open the app in your browser. It should look something like this:

  .. image:: images/tabbycat-bare.png

4. Import tournament data locally
---------------------------------

.. note:: Steps 4 and 5 are optional; there are other methods of :ref:`importing data <importing-initial-data>`. However the following method is most useful for large tournaments where manual entry would be tedious.

.. rst-class:: spaced-list

a. Place your CSV files in ``data/yourtournamentname``, as described in :ref:`importing-initial-data`.

b. Create a new, blank local database, and reconfigure ``DATABASES`` in your local_settings.py file to point to this new database.

c. Activate your virtual environment::

    source venv/bin/activate

d. Run initial migrations on your blank local database::

    dj migrate
    dj createsuperuser

e. Import your tournament data into your blank local database::

    dj importtournament <yourtournamentname> --name <Your Tournament Name> --short-name <Tournament>

  If your data's not clean, it might take a few attempts to get this right. We recommend either destroying and recreating the database (``dropdb``, ``createdb``), or wiping it using ``dj flush``, before retrying.

f. Check it looks like how you expect it to look, by starting your local installation::

    dj runserver

5. Push the local database to Heroku
------------------------------------

Once you're happy with how your local import went, you can push the local database to Heroku.

.. danger:: This step wipes the Heroku database clean, and replaces it with the contents of your local database. If you have any data on the Heroku site that isn't also in your local database, **that data will be lost** and will not be recoverable.

.. tip:: If you have multiple Heroku sites, you may find that the ``heroku`` commands refuse to run, prompting you to specify an app. If so, add ``--app <yourappname>`` to each ``heroku`` command.

a. Enable maintenance mode::

    heroku maintenance:on

b. Reset the database. (Caution: This permanently deletes all information on your Heroku database!)

  ::

    heroku pg:reset

c. Push your local database to Heroku::

    heroku pg:push <yourlocaldatabasename> DATABASE

  You might need to specify your local PostgreSQL credentials by adding ``PGUSER=<yourusername> PGPASSWORD=******** PGHOST=localhost`` to the *front* of that command.

d. Disable maintenance mode::

    heroku maintenance:off


Heroku options you may want to change
=====================================

If you have a large tournament, you may want to customize your Heroku app. This section provides some guidance on upgrades and settings you may wish to consider. Some of these configurations require you to have the `Heroku Command Line Interface (CLI) <https://devcenter.heroku.com/articles/heroku-cli>`_ installed.

Upgrading your database size
----------------------------

The free plan of `Heroku Postgres <https://elements.heroku.com/addons/heroku-postgresql>`_, "Hobby Dev", should work for most small tournaments. For large tournaments, however, you may find that you exceed the 10,000-row limit of this plan. It's difficult to give general guidance on how many rows you're likely to use, because it depends on which features of Tabbycat you use (*e.g.*, if you use adjudicator feedback). But to give some idea:

- Australs 2016, which had 74 teams, 8 preliminary rounds and heavily used adjudicator feedback, ended up at around 30,000 rows.
- The Asia BP championships 2017 had 100 teams, 6 preliminary rounds, and mandatory feedback (i.e. 100% return rates) used 15,000 rows.
- A 3 vs 3 tournament with 54 teams, 5 preliminary rounds, and which only lightly used adjudicator feedback ended up using around 4,500 rows

If you need more than 10,000 rows, you'll need to upgrade to a paid Heroku Postgres Plan. The 10,000,000 rows allowed in the lowest paid plan, "Hobby Basic", should certainly be more than sufficient.

If you're not sure, you can always start at Hobby Dev—just be prepared to `upgrade <https://devcenter.heroku.com/articles/upgrade-heroku-postgres-with-pgbackups>`_ during the tournament if you run close to capacity.

Custom domain names
-------------------

Your Heroku app will be available at ``yourappname.herokuapp.com``. You may want it to be a subdomain of your tournament's website, like ``tab.australasians2015.org``. If so, you'll need to configure your custom domain and SSL. Instructions for both are in the Heroku Dev Center:

- `Custom Domain Names for Apps <https://devcenter.heroku.com/articles/custom-domains>`_
- `Heroku SSL <https://devcenter.heroku.com/articles/ssl>`_

The custom domain name basically requires two things: a DNS ``CNAME`` entry on your website targeting ``yourappname.herokuapp.com``, and the custom domain configured on Heroku using ``heroku domains:add tab.yourwebsite.com``.  You'll also need to provide an SSL certificate for your custom domain and add it using the ``heroku certs:add`` command.

HTTPS
-----

Starting from version 1.3, all Tabbycat sites deployed to Heroku will redirect all traffic to HTTPS by default.

For a myriad of reasons, we strongly advise against disabling this. But if for some reason you need to run on plain HTTP, you can do this by setting the ``DISABLE_HTTPS_REDIRECTS`` config variable in Heroku to ``disable`` (see `Heroku documentation on config vars <https://devcenter.heroku.com/articles/config-vars>`_). The value of the config var must be ``disable``; if it's anything else, HTTPS redirects will remain in place.

.. tip:: Most modern browsers, after having been redirected by a site to HTTPS once, remember that that site requires HTTPS and go there for all subsequent visits even if the user typed in a plain http\:// address. It may do this because it cached the HTTP 301 permanent redirect, stored an HSTS entry and/or tagged its session cookie to require HTTPS. If, after disabling HTTPS on your Tabbycat site, you find that you're still being redirected to HTTPS, first try a browser or computer that *hasn't* visited the site before. If that works, then remove the relevant entry from your (original) browser's cache, HSTS set and cookies, and try again.
