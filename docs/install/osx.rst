.. _install-osx:

===========================
Installing Locally on macOS
===========================

.. admonition:: Is this the best installation method for you?
  :class: attention

  In most cases, we recommend doing an :ref:`internet-based installation on Heroku <install-heroku>` instead. If you decide to do a local installation, be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

  If you just want to quickly set up a copy of Tabbycat to run locally on macOS, consider :ref:`installing using Docker<install-docker>`, which is a shorter process than the one below.

Requisite technical knowledge
================================================================================

You need to be familiar with command-line interfaces to get through this comfortably. While a background in the specific tools Tabbycat uses (Python, PostgreSQL, *etc.*) will make things easier, it's not necessary: we'll talk you through the rest. You just need to be prepared to bear with us. It'll take a while the first time, but it gets easier after that.

Every line in the instructions that begins with ``$`` is a command that you need to run in a **Terminal**, but without the ``$``: that sign is a convention used in instructions to make it clear that it is a command you need to run.

.. admonition:: Advanced users
  :class: tip

  If you wish to use an SQL engine other that PostgreSQL, most of Tabbycat should work, but a few features rely on SQL functions that aren't supported by all engines. To configure Tabbycat to use a different engine, set the ``DATABASES`` `Django setting <https://docs.djangoproject.com/en/2.2/ref/settings/#databases>`_ accordingly.

1. Install dependencies
================================================================================

First, you need to install all of the software on which Tabbycat depends, if you don't already have it installed.

1(a). Python
--------------------------------------------------------------------------------
Tabbycat requires Python 3.9. macOS only comes with Python 2.7, so you'll need to install this. You can download the latest version from the `Python website <https://www.python.org/downloads/>`_.

The executable will probably be called ``python3``, rather than ``python``. Check::

    $ python3 --version
    Python 3.9.12

.. warning:: Tabbycat does not support Python 2. You must use Python 3.9.

You'll also need to install `Pipenv <https://pipenv.pypa.io/en/latest/>`_::

    $ pip install --user pipenv

(If you don't have `pip`, install it `here <https://pip.pypa.io/en/stable/installation/>`_.)

1(b). Postgres.app
--------------------------------------------------------------------------------

Download `Postgres.app <http://postgresapp.com/>`_, move it to your Applications folder, and open it. This should place an icon in your menu bar, showing that the postgres database is running. Whenever you are running Tabbycat you'll need to have this app running.

You'll need to use the PostgreSQL command-line tools, so run the command that the Postgres.app suggests in its `installation instructions <http://postgresapp.com/documentation/install.html>`_ for adding them to your ``$PATH``. As of February 2018, it was::

  sudo mkdir -p /etc/paths.d && echo /Applications/Postgres.app/Contents/Versions/latest/bin | sudo tee /etc/paths.d/postgresapp

1(c). Node.js/NPM
--------------------------------------------------------------------------------

Download and run the `node.js 8 macOS Installer (.pkg) <https://nodejs.org/dist/v12.18.1/node-v12.18.1.pkg>`_

2. Get the source code
================================================================================

a. `Go to the page for our latest release <https://github.com/TabbycatDebate/tabbycat/releases/latest>`_.
b. Download the zip or tar.gz file.
c. Extract all files in it to a folder of your choice.

.. admonition:: Advanced users
  :class: tip

  If you've used Git before, you might prefer to clone `our GitHub repository`_ instead. Don't forget to check out the |vrelease| tag or the master branch.

  Even better, you might like to fork the repository first, to give yourself a little more freedom to make code changes on the fly (and potentially :ref:`contribute <contributing>` them to the project).

3. Set up a new database
================================================================================

.. hint:: You can skip steps 1--3 if this is not your first installation. Every Tabbycat installation requires its own database, but they can use the same login role if you like.

a. Open up a copy of the Terminal app, then copy/paste or type in::

    $ sudo mkdir -p /etc/paths.d && echo /Applications/Postgres.app/Contents/Versions/latest/bin | sudo tee /etc/paths.d/postgresapp

b. Hit enter then quit and reopen the Terminal app.

c. Create a new user account with a password, replacing ``myusername`` with whatever name you prefer. If you don't know what username to pick, use ``tabbycat``.

  ::

    $ createuser myusername --pwprompt

d. Create a new database, replacing ``mydatabasename`` with whatever name you prefer, probably the name of the tournament you're running::

    $ createdb mydatabasename --owner myusername

e. In terminal type in::

    $ PATH="/Applications/Postgres.app/Contents/Versions/9.6/bin:$PATH"

4. Install Tabbycat
================================================================================
Almost there!

a. Navigate to your Tabbycat directory::

    $ cd path/to/my/tabbycat/directory

b. Copy **settings/local.example** to **settings/local.py**. Find this part in your new **local.py**, and fill in the blanks as indicated:

  .. code:: python

     DATABASES = {
         'default': {
             'ENGINE'  : 'django.db.backends.postgresql',
             'NAME'    : '',  # put your PostgreSQL database's name in here
             'USER'    : '',  # put your PostgreSQL login role's user name in here
             'PASSWORD': '',  # put your PostgreSQL login role's password in here
             'HOST':     'localhost',
             'PORT':     '5432',
         }
     }

  Optionally, replace the value in this line in the same file with your own time zone, as defined in the `IANA time zone database <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List>`_ (*e.g.*, ``Pacific/Auckland``, ``America/Mexico_City``, ``Asia/Kuala_Lumpur``)::

    TIME_ZONE = 'Australia/Melbourne'

c. Ensure you are in the main Tabbycat directory (not the config folder where **settings_local.py** is). Install the Python packages specified in the Pipfile using `Pipenv <https://pipenv.pypa.io/en/latest/>`_ (this also creates a virtual environment), and install the Node.js packages specified in package.json using `npm`::

    $ pipenv install --deploy
    $ npm ci

d. Start a Pipenv shell::

    $ pipenv shell

  You'll notice a prefix that looks like ``(tabbycat-9BkbSRuB)`` (except the random characters for you will be different). That means you're inside the Pipenv shell. Everything from this point onwards will be inside the Pipenv shell.

e. Navigate to the **tabbycat** sub-directory, initialize the database, compile the assets, and create a user account for yourself::

    (tabbycat-9BkbSRuB) $ cd tabbycat
    (tabbycat-9BkbSRuB) $ dj migrate
    (tabbycat-9BkbSRuB) $ npm run build
    (tabbycat-9BkbSRuB) $ dj collectstatic
    (tabbycat-9BkbSRuB) $ dj createsuperuser

f. Start Tabbycat!

  ::

    (tabbycat-9BkbSRuB) $ npm run serve

  Lots of text will flow by---this command starts up all of the processes necessary to run Tabbycat. But the app will be at http://127.0.0.1:8000/ or http://localhost:8000/ (not at any of the other addresses that will show).

g. Open your browser and go to http://127.0.0.1:8000/ or http://localhost:8000/. It should look something like the screenshot below. If it does, great! You've successfully installed Tabbycat.

  .. image:: images/tabbycat-bare.png
      :alt: Bare Tabbycat installation

Naturally, your database is currently empty, so proceed to :ref:`importing initial data <importing-initial-data>`.

Starting up an existing Tabbycat instance
=========================================
To start your Tabbycat instance up again next time you use your computer::

    $ cd path/to/my/tabbycat/directory
    $ pipenv run npm run serve

Or you can start a ``pipenv shell``, then run ``npm run serve`` from inside the Pipenv shell.
