.. _install-heroku:

====================
Installing on Heroku
====================

.. admonition:: IMPORTANT
  :class: error

  Unfortunately, due to Heroku policy, the "Deploy to Heroku" button for Tabbycat will not work. If you are unable to use `Calico <https://calicotab.com>`_, you can try:

  - Any of the Local installation methods
  - Using the instructions below as an alternative way to create a Heroku site
  - Our (in beta) `support for Render <https://tabbycat.readthedocs.io/en/latest/install/render.html>`_, which uses a similar 1-click method

Heroku Deployments
==================

*We've tested these instructions successfully on Windows, Linux and macOS.*

Requisite technical background
------------------------------

You will need to (briefly) work with a command-line interfaces to complete this method.
When we say "command-line", on Windows we mean **Command Prompt**, and on Linux and macOS we mean **Terminal** (or your favourite command shell).

If you haven't used a command-line interface before, you may want to watch a very general and introductory tutorial. We will be providing the commands for you to enter, but you will need to know where to find the command-line and how to put text into it.

If you're experienced with the command-line and Git, :ref:`skip ahead to our TLDR list of commands <tldr>`.

Account Setup
-------------

`Heroku <http://www.heroku.com/>`_ is a platform as a service on which Tabbycat can be installed to be available on the internet. Naturally, this requires you to have a Heroku account. Head to the site and sign-up for one.

.. note:: During the setup process, Heroku will ask you to verify your account by adding a credit card. A standard Tabbycat site *will not charge* your card — charges only accrue if you deliberately add a paid service in the Heroku dashboard.

1. Install dependencies
-----------------------

Install the `Heroku Command Line Interface (CLI) <https://devcenter.heroku.com/articles/heroku-cli>`_, then log in by running this in your command-line (and entering in your Heroku account details)::

    heroku login

If you don't already have **Git**, follow the `instructions on the GitHub website <https://help.github.com/articles/set-up-git>`_ to set up Git.

2. Download Tabbycat with Git
-----------------------------

Once git is installed, you can use it to download a copy of Tabbycat with these commands in your command-line::

    git clone -b master https://github.com/TabbycatDebate/tabbycat.git

3. Run the Deploy Script
------------------------

.. rst-class:: spaced-list

a. Navigate on the command-line your Tabbycat directory. If you have not changed directories in the command-line since you cloned Tabbycat, this should just be::

    cd tabbycat

b. Run the script to deploy the app to Heroku. Replace ``yourappname`` with your preferred URL. Your website will be at ``yourappname.herokuapp.com``.

  ::

    python deploy_heroku.py yourappname

  This script has other options that you might find useful. Run ``python deploy_heroku.py --help`` for details.

  The script may work away on its own for 10-30 minutes before it asks you some questions to answer. When finished, it will open the app in your browser. It should look something like this:

  .. image:: images/tabbycat-bare.png

That's everything! You can then login with the account that you made by answering the script's questions.

.. _tldr:

TLDR commands
-------------

.. warning:: We provide a "short version" for experienced users. Don't just copy and paste these commands before you understand what they do! If things aren't set up perfectly they can fail, so it's important to supervise them the first time you do them. If this is all new to you, read the long version of the instructions below.

.. parsed-literal::

  git clone https\:\/\/github.com/TabbycatDebate/tabbycat.git
  cd tabbycat
  git checkout master
  python deploy_heroku.py yourappname

Heroku options you may want to change
=====================================

If you have a large tournament, you may want to customize your Heroku app. This section provides some guidance on upgrades and settings you may wish to consider. Some of these configurations require you to have the `Heroku Command Line Interface (CLI) <https://devcenter.heroku.com/articles/heroku-cli>`_ installed.

.. _db-upgrades:

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

If you're using Tabbycat's email notifications, you might also configure your email provider to use domain authentication---see :ref:`configuring-email-provider`.

Time zone
---------

If you want to change the time zone you nominated during deployment, you can do so by going to the `Heroku Dashboard <https://dashboard.heroku.com/>`_, clicking on your app, going to the **Settings** tab, clicking **Reveal Config Vars** and changing the value of the ``TIME_ZONE`` variable. This value must be one of the names in the IANA tz database, *e.g.* ``Pacific/Auckland``, ``America/Mexico_City``, ``Asia/Kuala_Lumpur``.  You can find a `list of these on Wikipedia <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List>`_ in the 'TZ\*' column.

Email provider
--------------

  *Changed in version 2.6:* Tabbycat no longer automatically provisions SendGrid via Heroku.

Tabbycat does not come with an email provider. Before Tabbycat will send emails, you will need to install a third-party email provider yourself. To do so, you may add/change the following config vars:

- ``DEFAULT_FROM_EMAIL``: Email to send from
- ``EMAIL_HOST``: Host server
- ``EMAIL_HOST_USER``: Username for authentification to host
- ``EMAIL_HOST_PASSWORD``: Password with username
- ``EMAIL_PORT`` (default 587): Port for server
- ``EMAIL_USE_TLS`` (default True): Whether to use `Transport Layer Security <https://en.wikipedia.org/wiki/Transport_Layer_Security>`_ (True/False)

See :ref:`configuring-email-provider` for more information, including a few options for email service providers.

.. _upgrade-heroku:

Upgrading an existing Heroku app
================================

.. note:: For most users, we recommend starting a new site for every tournament, when you set up the tab for that tournament. There's generally not a pressing need to upgrade Tabbycat after a tournament is concluded, and every time you deploy a new site, you'll be using the latest version at the time of deployment.

To upgrade an existing Heroku-based Tabbycat app to the latest version, you need to *deploy* the current version of Tabbycat to your Heroku app. There are several ways to do this. We list one below, primarily targeted at users with some background in Git.

The essence of it is that you need to `create a Git remote <https://devcenter.heroku.com/articles/git#creating-a-heroku-remote>`_ for your Heroku app (if you don't already have one), then `push to it <https://devcenter.heroku.com/articles/git#deploying-code>`_.

.. attention:: You should **always** :ref:`back up your database <backups>` before upgrading Tabbycat.

You'll need both Git and the Heroku CLI, and you'll need to be logged in to the Heroku CLI already.

1. Take a backup of your database::

    $ heroku pg:backups:capture

2. If you haven't already, clone our Git repository and check out the master branch::

    $ git clone https\:\/\/github.com/TabbycatDebate/tabbycat.git
    $ git checkout master

  If you've already cloned our Git repository, don't forget to pull so you're up to date::

    $ git checkout master
    $ git pull

3. Check to see if you have a Git remote already in place::

    $ git remote -v
    heroku  https://git.heroku.com/mytournament2018.git (fetch)
    heroku  https://git.heroku.com/mytournament2018.git (push)

  If you do, the name of the remote will be on the left (``heroku`` in the above example), and the URL of your Git repository will be on the right. In the example above, our Tabbycat site URL would be ``mytournament2018.herokuapp.com``; the Git remote URL is then ``https://git.heroku.com/mytournament2018.git``.

  If a Git remote URL for your Tabbycat site *doesn't* appear, then create one::

    $ heroku git:remote --app mytournament2018 --remote heroku
    set git remote heroku to https://git.heroku.com/mytournament2018.git

  .. tip:: If you tab many tournaments, it'll probably be helpful to use a name other than ``heroku`` (say, ``mytournament2018``), so that you can manage multiple tournaments.

4. Push to Heroku::

    $ git push heroku master

  This will take a while to complete.
