.. _install-heroku:

====================
Installing on Heroku
====================

When running Tabbycat on the internet, we set it up on `Heroku <http://www.heroku.com/>`_. The project is set up to be good to go on Heroku, and it works well for us, so if you'd like to run it online, we recommend that you do the same. Naturally, this requires you to have a Heroku account.

We've tested these instructions successfully on Windows, Linux and Mac OS.

Requisite technical background
==============================

You need to have at least a passing familiarity with command-line interfaces to get through this. We'll talk you through the rest.

When we say "command shell", on Windows we mean **Command Prompt**, and on Linux and OS X we mean **Terminal** (or your favourite command shell).

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a `Django <https://www.djangoproject.com/>`_ project. As such, it can be installed on any web platform that supports Django, using any SQL system that Django supports. Just be aware that we haven't tried any other platform.

Installation
============

Short version
-------------
::

  git clone https://github.com/czlee/tabbycat.git
  cd tabbycat
  python deploy_heroku.py <yourappname>

If you want to :ref:`import tournament data <importing-initial-data>` from CSV files, put them in ``data/<yourtournamentname>``, then::

  git commit -am "Add data for <yourtournamentname>"
  git push heroku master
  heroku run dj importtournament <yourdatadirectoryname> --slug <slug> --name <Your Awesome Tournament> --short-name <Awesome>

1. Install dependencies
-----------------------

- Go to `toolbelt.heroku.com <https://toolbelt.heroku.com/>`_ and install the **Heroku Toolbelt**. Then open a command shell and log in using ``heroku login``.

- Windows users need to install **Python**. Follow the instructions in (only!) :ref:`part 1(a) of our Windows instructions <install-python-windows>`.

- If you don't already have **Git**, follow the `instructions on the GitHub website <https://help.github.com/articles/set-up-git>`_ to set up Git.

.. note:: Linux and OS X users probably already have Python installed. There is no need to install Python 3 specifically. Although Tabbycat uses Python 3, installing it on Heroku relies only on the deployment script, which is compatible with both Python 2 and Python 3.

2. Get the source code
----------------------
Open a command shell. Navigate to an appropriate directory on your computer using ``cd`` (creating directories using ``mkdir`` as appropriate), then run this command::

  git clone https://github.com/czlee/tabbycat.git

.. tip:: If this is your second time creating a Tabbycat instance on Heroku from this computer, you don't need to clone the repository a second time. Just run ``git pull`` to update the code to the latest version, and press ahead to step 3: Deploy to Heroku.

3. Deploy to Heroku
-------------------

1. Navigate to your Tabbycat directory::

    cd path/to/my/tabbycat

2. Run the script to deploy the app to Heroku. Replace ``<yourappname>`` with your preferred URL. Your website will be at ``<yourname>.herokuapp.com``.

  ::

    python deploy_heroku.py <yourappname>

  This script has other options that you might find useful. Run ``python deploy_heroku.py --help`` for details.

  .. note:: If you'd prefer to import tournament data locally and `push <https://devcenter.heroku.com/articles/heroku-postgresql#pg-push>`_ the database to Heroku using ``heroku pg:push``, use the ``--no-init-db`` option to prevent ``deploy_heroku.py`` from running initial migrations on the database.

  .. note:: If this isn't your first tournament, the ``heroku`` Git remote might already be pointing to your first tournament. In this case, you should use the ``--git-remote <new_remote_name>`` option to get the script to create a new git remote for you, so you can use when importing tournament data.

  When this script finishes, it will open the app in your browser. It should look something like this:

  .. image:: images/tabbycat-bare.png

4. Import tournament data
-------------------------

.. note:: This step is optional and there are other methods of :ref:`importing data <importing-initial-data>`. However the following method is most useful for large tournaments where manual entry would be tedious.

In order to use the ``importtournament`` command directly on the server, your data also needs to be on the server. The easiest way to get this data on to the server is to make a Git commit and ``git push`` it to the server.

1. Place your CSV files in ``data/yourtournamentname``, as described in :ref:`importing-initial-data`.

2. Commit and push::

    git commit -am "Add data for <yourtournamentname>"
    git push heroku master

  .. note:: If you use ``--git-remote`` in step 3 to create your own Git remote, you should use that remote name instead of ``heroku`` in the last command above.

  .. admonition:: Advanced users
    :class: tip

    You might like to create a new branch to keep this data off your master branch.

3. Run this command, replacing ``<fields>`` with your own names::

    heroku run dj importtournament <yourdatadirectoryname> --slug <slug> --name <Your Awesome Tournament> --short-name <Awesome>

Addons
======

For Australs 2014, we found that the ``hobby-dev`` plan of `Heroku Postgres <https://elements.heroku.com/addons/heroku-postgresql>`_ didn't allow for more than 10,000 database rows, so we upgraded to ``hobby-basic``, which was enough (and costs a few dollars). At the end of that tournament, we had about 20,000 rows. For similar-sized tournaments (84 teams, 8 prelim rounds), you'll probably find your usage about the same, wheras small tournaments should fit within the 10,000 row limit easily.

If you're not sure, you can always start at ``hobby-dev``—just be prepared to `upgrade <https://devcenter.heroku.com/articles/upgrade-heroku-postgres-with-pgbackups>`_ during the tournament if you run close to capacity.

Custom Domain Names
===================

Your Heroku app will be available at *yourappname.herokuapp.com*. You may want it to be a subdomain of your tournament's website, like `tab.australasians2015.org <http://tab.australasians2015.org>`_. Instructions for this are `in the Heroku documentation <https://devcenter.heroku.com/articles/custom-domains>`_. Basically there are two things to do:

1. Add a DNS entry to your website, with record ``CNAME``, name ``tab`` (or whatever you prefer) and target ``yourappname.herokuapp.com``. You'll need to figure out how to do this with your tournament website hosting service (which is probably not Heroku).

2. Add a custom subdomain to Heroku, like this::

    heroku domains:add tab.yourwebsite.com