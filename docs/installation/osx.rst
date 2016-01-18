.. _install-osx:

==========================
Installing locally on OS X
==========================

Before you start, be sure to read our general information on [[local installations]] to help you understand what's going on.

Requisite technical knowledge
================================================================================

You need to be familiar with command-line interfaces to get through this comfortably. While a background in the specific tools (Python, *etc.*) we use will make things easier for you, it's not necessary: we'll talk you through the rest. You just need to be prepared to bear with us. It'll take a while the first time, but it gets easier after that.

Every line in the instructions that begins with ``$`` is a command that you need to run in a **Terminal**, but without the ``$``: that sign is a convention used in instructions to make it clear that it is a command you need to run.

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a Django project, so can be installed in any manner that Django projects can normally be installed. For example, if you prefer some SQL system other than PostgreSQL, you can use it so long as it's Django-compatible. Just be aware that we might not have tried it.

1. Install dependencies
================================================================================

First, you need to install all of the software on which Tabbycat depends, if you don't already have it installed.

1(a). Python
--------------------------------------------------------------------------------
As of version 0.8, Tabbycat requires Python 3.4 or later. OS X only comes with Python 2.7, so you'll need to install this. You can download the latest version from the `Python website <https://www.python.org/downloads/>`_.

The executable will probably be called `python3`, rather than `python`. Check::

    $ python3 --version
    Python 3.4.4

.. warning:: As of version 0.8, Python 2 is not supported. You must use Python 3.4 or
  higher.

.. admonition:: Advanced users
  :class: tip

  These instructons will use the ``pyvenv`` module. If you prefer, you can use `Virtualenv <https://virtualenv.pypa.io/en/latest/installation.html>`_ instead.

1(b). PostgreSQL
--------------------------------------------------------------------------------

There are instructions on `this blog post <https://marcinkubala.wordpress.com/2013/11/11/postgresql-on-os-x-mavericks/>`_ for installing PostgreSQL on OS X.

2. Get the source code
================================================================================

There are two ways to get the source code: by using Git, or by downloading a release zip file. If you can, we encourage you to use Git. It'll be easier to keep up to date with Tabbycat and to deploy to a Heroku installation later. However, Git can be confusing for first-timers, so if you just want to get going, the zip file will do fine.

Option 1: Clone the Git repository
--------------------------------------------------------------------------------

1. If you don't already have Git, follow the `instructions on the GitHub website <https://help.github.com/articles/set-up-git>`_ to set up Git.
2. Clone the repository::

    $ git clone https://github.com/czlee/tabbycat.git

.. tip:: If you have a GitHub account, you might like to fork the repository first, to give yourself a little more freedom.


Option 2: Download a release package
--------------------------------------------------------------------------------

1. `Go to our release packages page <https://github.com/czlee/tabbycat/releases>`_.
2. Download the latest zip or tar.gz file.
3. Extract all files in it to a folder of your choice.

3. Set up a new database
================================================================================

.. hint:: You can skip step 1 if this is not your first installation. Every Tabbycat installation requires its own database, but they can use the same login role if you like.

1. Create a new user account with a password, replacing ``myusername`` with whatever name you prefer. If you don't know what username to pick, use ``tabbycat``.

  ::

    $ sudo -u postgres createuser myusername --pwprompt

  .. tip:: If you'll be running multiple instances of Tabbycat, developing, or diving into the database yourself, you might find it convenient to set up client authentication so that you don't need to do all manual operations from ``sudo -u postgres``. See the `PostgreSQL documentation on client authentication <http://www.postgresql.org/docs/9.4/static/client-authentication.html>`_ for more information. For example, you could add a ``local all myusername md5`` line to the ``pg_hba.conf`` file, or you could define a mapping in ``pg_ident.conf`` and append the ``map=`` option to the ``local all all peer`` line. If you want your new PostgreSQL account to be able to create databases, add ``--createdb`` to the above command.

2. Create a new database, replacing ``mydatabasename`` with whatever name you prefer, probably the name of the tournament you're running::

    $ sudo -u postgres createdb mydatabasename --owner myusername

4. Install Tabbycat
================================================================================
Almost there!

1. Navigate to your Tabbycat directory::

    $ cd path/to/my/tabbycat

2. Copy **local_settings.example** to **local_settings.py**. Find this part in your new local_settings.py, and fill in the blanks as indicated:

  .. code:: python

     DATABASES = {
         'default': {
             'ENGINE'  : 'django.db.backends.postgresql_psycopg2',
             'NAME'    : '',  # put your PostgreSQL database's name in here
             'USER'    : '',  # put your PostgreSQL login role's user name in here
             'PASSWORD': '',  # put your PostgreSQL login role's password in here
             'HOST':     'localhost',
             'PORT':     '5432',
         }
     }

3. Start a new virtual environment. We suggest the name ``venv``, though it can be any name you like::

    $ pyvenv venv

4. Run the ``activate`` script. This puts you "into" the virtual environment::

    $ source venv/bin/activate

5. Install Tabbycat's requirements into your virtual environment::

    $ pip install --upgrade pip
    $ pip install -r requirements_common.txt

  .. warning:: If on OS X 10.9+ or using XCode 5.1+, installing ``psycopg2`` may fail. In that case, run the following::

      $ ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install -r requirements_common.txt

6. Initialize the database and create a user account for yourself::

    $ dj migrate
    $ dj createsuperuser

7. Start Tabbycat!

  ::

    $ dj runserver

  It should show something like this::

    System check identified no issues (0 silenced).

    January 17, 2016 - 10:12:11
    Django version 1.9.1, using settings 'settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

8. Open your browser and go to the URL printed above. (In the above example, it's http://127.0.0.1:8000/.) It should look something like the screenshot below. If it does, great! You've successfully installed Tabbycat.

  .. image:: images/tabbycat-bare-linux.png
      :alt: Bare Tabbycat installation
.. TODO Replace this with a screenshot of OS X


Naturally, your database is currently empty, so proceed to :ref:`importing initial data <importing-initial-data>`.

Starting up an existing Tabbycat instance
================================================================================
To start your Tabbycat instance up again next time you use your computer::

    $ cd path/to/my/tabbycat
    $ source venv/bin/activate
    $ dj runserver
