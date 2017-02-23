.. _install-heroku:

====================
Installing on Heroku
====================

When running Tabbycat on the internet, we set it up on `Heroku <http://www.heroku.com/>`_. The project is set up to be good to go on Heroku, and it works well for us, so if you'd like to run it online, we recommend that you do the same. Naturally, this requires you to have a Heroku account.

Installation---the short way
============================
Click this button:

.. image:: https://www.herokucdn.com/deploy/button.svg
  :target: https://heroku.com/deploy?template=https://github.com/czlee/tabbycat/tree/master

This is the easiest way to deploy an instance of Tabbycat online. It requires no technical background.

If you don't already have a Heroku account, it'll prompt you to create one. Once you're logged in to Heroku, choose a name for your installation, then scroll down and click **Deploy**. Once it's finished, click **View** and follow the prompts. Once finished, open the site and from there you can easily set up a demo data set (if you just want to learn Tabbycat) or use the data importer to set up a real tournament.

.. note:: During the setup process Heroku will ask you to verify your account by adding a credit or debit card. A standard Tabbycat site *will not charge* your card without explicit permission — charges only accrue if you deliberately add a paid service in the Heroku dashboard.

  That said if you do not have access to a credit/debit card we offer a version of the software — 'Tabbykitten' — that does not require Heroku to verify your account. However, as a result, this version is limited: it does not send error reports to the developers and can handle much less public traffic. We strongly recommend using it only as a last resort, and even then only for small tournaments. `Use this link to set up a Tabbykitten site <https://heroku.com/deploy?template=https://github.com/czlee/tabbycat/tree/kitten&env[KITTEN]=true>`_.

If you have a background in programming, you might prefer the method below.

Installation---the long way
===========================
The long way sets you up with more control over your environment. Because you'll clone `our GitHub repository`_, it'll be easier for you to pull and contribute updates to the source code.  We recommend it if you have experience with Git.  It's also easier with this method to import CSV files using the command-line importer, so if you have a very large tournament, this might make importing initial data easier.

We've tested these instructions successfully on Windows, Linux and Mac OS.

Requisite technical background
------------------------------

You need to have at least a passing familiarity with command-line interfaces to get through the longer traditional method. We'll talk you through the rest.

When we say "command shell", on Windows we mean **Command Prompt**, and on Linux and OS X we mean **Terminal** (or your favourite command shell).

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a `Django <https://www.djangoproject.com/>`_ project. As such, it can be installed on any web platform that supports Django, using any SQL system that Django supports. Just be aware that we haven't tried any other platform.

Short version
-------------
.. parsed-literal::

  git clone https\:\/\/github.com/czlee/tabbycat.git
  git checkout |vrelease|                               # or master
  cd tabbycat
  python deploy_heroku.py <yourappname>

If you want to :ref:`import tournament data <importing-initial-data>` from CSV files, put them in ``data/<yourtournamentname>``, then::

  git commit -am "Add data for <yourtournamentname>"
  git push heroku master
  heroku run tabbycat/manage.py importtournament <yourdatadirectoryname> --slug <slug> --name <Your Awesome Tournament> --short-name <Awesome>

1. Install dependencies
-----------------------

- Install the `Heroku Command Line Interface (CLI) <https://devcenter.heroku.com/articles/heroku-cli>`_. Then open a command shell and log in using ``heroku login``.

- Windows users need to install **Python**. Follow the instructions in (only!) :ref:`part 1(a) of our Windows instructions <install-python-windows>`.

- If you don't already have **Git**, follow the `instructions on the GitHub website <https://help.github.com/articles/set-up-git>`_ to set up Git.

.. note:: Linux and OS X users probably already have Python installed. There is no need to install Python 3 specifically. Although Tabbycat uses Python 3, installing it on Heroku relies only on the deployment script, which is compatible with both Python 2 and Python 3.

2. Get the source code
----------------------
Open a command shell. Navigate to an appropriate directory on your computer using ``cd`` (creating directories using ``mkdir`` as appropriate), then run:

.. parsed-literal::

  git clone https\:\/\/github.com/czlee/tabbycat.git
  git checkout |vrelease|                               # or master


.. tip:: If this is your second time creating a Tabbycat instance on Heroku from this computer, you don't need to clone the repository a second time. Just run ``git pull`` to update the code to the latest version, and press ahead to step 3: Deploy to Heroku.

3. Deploy to Heroku
-------------------

1. Navigate to your Tabbycat directory::

    cd path/to/my/tabbycat/directory

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

    heroku run tabbycat/manage.py importtournament <yourdatadirectoryname> --slug <slug> --name <Your Awesome Tournament> --short-name <Awesome>

Heroku options you may want to change
=====================================

If you have a large tournament, you may want to customize your Heroku app. This section provides some guidance on upgrades and settings you may wish to consider. Some of these configurations require you to have the `Heroku Command Line Interface (CLI) <https://devcenter.heroku.com/articles/heroku-cli>`_ installed.

Upgrading your database size
----------------------------

The free plan of `Heroku Postgres <https://elements.heroku.com/addons/heroku-postgresql>`_, "Hobby Dev", should work for most small tournaments. For large tournaments, however, you may find that you exceed the 10,000-row limit of this plan. It's difficult to give general guidance on how many rows you're likely to use, because on which features of Tabbycat you use (*e.g.*, if you use adjudicator feedback). But to give some idea, Australs 2016, which had 74 teams and 8 preliminary rounds and used adjudicator feedback, ended up at around 30,000 rows.

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
