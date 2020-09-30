.. _install-heroku:

====================
Installing on Heroku
====================

`Heroku <http://www.heroku.com/>`_ is a platform as a service on which Tabbycat can be installed to be available on the internet. Naturally, this requires you to have a Heroku account.

There are two ways to do this: a **short way** and a **long way**. Most people should use the short way. The long way requires some familiarity with command-line interfaces and Git, and requires a :ref:`local installation <install-local>` as a prerequisite, but makes it easier to :ref:`upgrade versions <upgrade-heroku>` later on and (unlike the short way) allows you to import data from CSV files.

The short way
=============
Click this button:

.. image:: https://www.herokucdn.com/deploy/button.svg
  :target: https://heroku.com/deploy?template=https://github.com/TabbycatDebate/tabbycat/tree/master

It requires no technical background.

If you don't already have a Heroku account, it'll prompt you to create one. Once you're logged in to Heroku, choose a name for your installation, then scroll down and click **Deploy**. Once it's finished, click **View** and follow the prompts. Once finished, open the site and from there you can easily set up a demo data set (if you just want to learn Tabbycat) or use the data importer to set up a real tournament.

.. note:: During the setup process, Heroku will ask you to verify your account by adding a credit card. A standard Tabbycat site *will not charge* your card — charges only accrue if you deliberately add a paid service in the Heroku dashboard.

  If you can't access a credit card, you can instead install a limited version, which we call "Tabbykitten". However, Tabbykitten is out-of-date, cannot send e-mails, and is less able to serve lots of simultaneous users. We therefore strongly recommend it only as a last resort, and even then only for small tournaments.  `Use this link to set up a Tabbykitten site <https://heroku.com/deploy?template=https://github.com/TabbycatDebate/tabbycat/tree/kitten>`_.

The long way
============
The long way sets you up with more control over your environment.  Because you'll clone `our GitHub repository`_, it'll be easier for you to :ref:`upgrade your app <upgrade-heroku>` when a new version is released.  You'll also have the flexibility to make and contribute updates to the source code.  We recommend it if you have experience with Git.  It's also easier with this method to import CSV files using the command-line importer, so if you have a very large tournament, this might make importing initial data easier.

We've tested these instructions successfully on Windows, Linux and macOS.

Requisite technical background
------------------------------

You need to have at least a passing familiarity with command-line interfaces to get through the longer traditional method. We'll talk you through the rest.

When we say "command shell", on Windows we mean **Command Prompt**, and on Linux and macOS we mean **Terminal** (or your favourite command shell).

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a `Django <https://www.djangoproject.com/>`_ project. As such, it can be installed on any web platform that supports Django, using PostgreSQL. Just be aware that requirements and installation may be slightly different.

Short version of the long way
-----------------------------

.. warning:: We provide a "short version" for experienced users. Don't just copy and paste these commands before you understand what they do! If things aren't set up perfectly they can fail, so it's important to supervise them the first time you do them. If this is all new to you, read the long version of the instructions below.

.. parsed-literal::

  git clone https\:\/\/github.com/TabbycatDebate/tabbycat.git
  cd tabbycat
  git checkout master
  python deploy_heroku.py yourappname

If you want to :ref:`import tournament data <importing-initial-data>` from CSV files, :ref:`install Tabbycat locally <install-local>`, put your CSV files in ``data/yourtournamentname``, then::

  createdb yourlocaldatabasename     # Your settings_local.py file must point here from DATABASES
  dj migrate
  dj createsuperuser
  dj importtournament yourtournamentname --name "Your Tournament Name" --short-name "Tournament"
  heroku maintenance:on
  heroku pg:reset
  heroku pg:push yourlocaldatabasename DATABASE
  heroku maintenance:off

1. Install dependencies
-----------------------

a. Install the `Heroku Command Line Interface (CLI) <https://devcenter.heroku.com/articles/heroku-cli>`_, then log in with the command ``heroku login``.

b. If you don't already have **Git**, follow the `instructions on the GitHub website <https://help.github.com/articles/set-up-git>`_ to set up Git.

2. Set up a local installation
------------------------------

If you don't already have a local installation, follow the instructions on the page for your operating system, listed below, to set up a local installation.

.. attention:: When downloading the source code, you **must** take the option involving cloning the GitHub repository using Git. In the macOS and Windows instructions, this means the option described in the "Advanced users" box. To do so, use these commands:

  .. parsed-literal::

      $ git clone https\:\/\/github.com/TabbycatDebate/tabbycat.git
      $ git checkout master

  Do not download the .tar.gz or .zip file and extract it.

- :ref:`install-linux`
- :ref:`install-osx`
- :ref:`install-wsl`
- :ref:`install-windows`

If you do already have a local installation, update to the latest version using:

.. parsed-literal::

    $ git checkout master
    $ git pull

.. admonition:: Advanced users
  :class: tip

  It's not *strictly* necessary to have a fully functional local installation if you don't want to import data from CSV files. But it certainly helps.

3. Deploy to Heroku
-------------------

.. rst-class:: spaced-list

a. Navigate to your Tabbycat directory::

    cd path/to/my/tabbycat/directory

b. Run the script to deploy the app to Heroku. Replace ``yourappname`` with your preferred URL. Your website will be at ``yourappname.herokuapp.com``.

  ::

    python deploy_heroku.py yourappname

  This script has other options that you might find useful. Run ``python deploy_heroku.py --help`` for details.

  When this script finishes, it will open the app in your browser. It should look something like this:

  .. image:: images/tabbycat-bare.png

4. Import tournament data locally
---------------------------------

.. note:: Steps 4 and 5 are optional; there are other methods of :ref:`importing data <importing-initial-data>`. However the following method is most useful for large tournaments where manual entry would be tedious.

.. note:: Step 4 is the same as the process described in :ref:`importtournament-command`.

.. rst-class:: spaced-list

a. Place your CSV files in ``data/yourtournamentname``, as described in :ref:`importing-initial-data`.

b. Create a new, blank local database::

    createdb yourlocaldatabasename

  It's normally easiest to name your local database after your app name, so that if you have multiple sites, you know which one relates to which.

  Reconfigure ``DATABASES`` in your settings_local.py file to point to this new database.

c. Activate your virtual environment::

    source venv/bin/activate

d. Run initial migrations on your blank local database::

    dj migrate
    dj createsuperuser

e. Import your tournament data into your blank local database::

    dj importtournament yourtournamentname --name "Your Tournament Name" --short-name "Tournament"

  If your data's not clean, it might take a few attempts to get this right. We recommend either destroying and recreating the database (``dropdb``, ``createdb``), or wiping it using ``dj flush``, before retrying.

f. Check it looks like how you expect it to look, by starting your local installation::

    dj runserver

5. Push the local database to Heroku
------------------------------------

Once you're happy with how your local import went, you can push the local database to Heroku.

.. danger:: This step wipes the Heroku database clean, and replaces it with the contents of your local database. If you have any data on the Heroku site that isn't also in your local database, **that data will be lost** and will not be recoverable.

.. tip:: If you have multiple Heroku sites, you may find that the ``heroku`` commands refuse to run, prompting you to specify an app. If so, add ``--app yourappname`` to each ``heroku`` command.

a. Enable maintenance mode. This takes the site offline, to ensure that no-one can possibly create or change any data on the site while you're pushing a new database up::

    heroku maintenance:on

b. Reset the database. (Caution: This permanently deletes all information on your Heroku database!)

  ::

    heroku pg:reset

c. Push your local database to Heroku::

    heroku pg:push yourlocaldatabasename DATABASE

  You might need to specify your local PostgreSQL credentials by adding ``PGUSER=yourusername PGPASSWORD=******** PGHOST=localhost`` to the *beginning* of that command. (This sets environment variables to those values for the duration of that one command.)

d. Disable maintenance mode::

    heroku maintenance:off


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

HTTPS
-----

All Tabbycat sites deployed to Heroku redirect all traffic to HTTPS by default.

For a myriad of reasons, we strongly advise against disabling this. But if for some reason you need to run on plain HTTP, you can do this by setting the ``DISABLE_HTTPS_REDIRECTS`` config variable in Heroku to ``disable`` (see `Heroku documentation on config vars <https://devcenter.heroku.com/articles/config-vars>`_). The value of the config var must be ``disable``; if it's anything else, HTTPS redirects will remain in place.

.. tip:: Most modern browsers, after having been redirected by a site to HTTPS once, remember that that site requires HTTPS and go there for all subsequent visits even if the user typed in a plain http\:// address. It may do this because it cached the HTTP 301 permanent redirect, stored an HSTS entry and/or tagged its session cookie to require HTTPS. If, after disabling HTTPS on your Tabbycat site, you find that you're still being redirected to HTTPS, first try a browser or computer that *hasn't* visited the site before. If that works, then remove the relevant entry from your (original) browser's cache, HSTS set and cookies, and try again.

Time zone
---------

If you want to change the time zone you nominated during deployment, you can do so by going to the `Heroku Dashboard <https://dashboard.heroku.com/>`_, clicking on your app, going to the **Settings** tab, clicking **Reveal Config Vars** and changing the value of the ``TIME_ZONE`` variable. This value must be one of the names in the IANA tz database, *e.g.* ``Pacific/Auckland``, ``America/Mexico_City``, ``Asia/Kuala_Lumpur``.  You can find a `list of these on Wikipedia <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List>`_ in the 'TZ\*' column.

SendGrid account details
------------------------

By default, Heroku will automatically create a SendGrid account for you. For small tournaments, this should work fine. For larger ones, though, SendGrid typically doesn't allow new accounts to send so many emails without additional vetting. This vetting is separate to the verification you did for your Heroku account, and as far as we're aware, it can't be done until you send your first email, by which time it's probably too late.

If you're running a large tournament, you may wish to use your own SendGrid account instead. The free tier probably won't suffice after the trial period, but the Essentials tier should be more than adequate. If you're a student and have the `GitHub Education Pack <https://education.github.com/pack>`_, you might find the SendGrid plan here useful.

If you set up and use your own SendGrid account, you can remove the SendGrid add-on from your Heroku app. The SendGrid add-on is only necessary if you wish to use Heroku's auto-created SendGrid account.

To set up your app to use your own SendGrid account:

.. rst-class:: spaced-list

1. `Sign up for a SendGrid account <https://sendgrid.com/pricing/>`_, if you don't already have one.

2. `Create an API key <https://app.sendgrid.com/settings/api_keys>`_ in your SendGrid account.

  There are `instructions for how to do this in the SendGrid documentation <https://sendgrid.com/docs/User_Guide/Settings/api_keys.html>`_. The only permission that is needed is the "Mail Send" permission, so you can turn off all others if you want to be safe.

3. Set the following config vars in Heroku Dashboard (or using the Heroku CLI, if you have it):

  - ``SENDGRID_USERNAME`` should be set to ``apikey`` (not your username).
  - ``SENDGRID_PASSWORD`` should be set to your API key, which will start with ``SG*******``.

  .. warning:: The `Heroku SendGrid instructions <https://devcenter.heroku.com/articles/sendgrid#setup-api-key-environment-variable>`_ to do something with ``SENDGRID_API_KEY`` are **incorrect**. We figured this out by contacting SendGrid support staff. Use the above config vars instead.


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
