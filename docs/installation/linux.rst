.. _install-linux:

===========================
Installing locally on Linux
===========================

Before you start, be sure to read our general information on :ref:`local installations <install-local>` to help you understand what's going on.

Requisite technical background
================================================================================

You need to be familiar with command-line interfaces to get through this comfortably. While a background in the specific tools (Python, *etc.*) we use will make things easier for you, it's not necessary: we'll talk you through the rest.

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a Django project, so can be installed in any manner that Django projects can normally be installed. For example, if you prefer some SQL system other than PostgreSQL, you can use it so long as it's Django-compatible. Just be aware that we might not have tried it.

1. Install dependencies
================================================================================
First, you need to install all of the software on which Tabbycat depends, if you don't already have it installed.

.. admonition:: Advanced users
  :class: tip

  **These instructions are for Ubuntu.** If you have another distribution of Linux, we trust you'll know how to navigate the package manager for your distribution to install the dependencies.

1(a). Python
--------------------------------------------------------------------------------
As of version 0.8, Tabbycat requires Python 3.4 or later. You probably already
have this installed, but it'll be called ``python3``. Check::

    $ python3 --version
    Python 3.4.3

If it's not installed, run ``sudo apt-get install python3``, or `download the latest version from the Python website <https://www.python.org/downloads/>`_.

.. warning:: As of version 0.8, Python 2 is not supported. You must use Python 3.4 or
  higher.

1(b). Pyvenv
--------------------------------------------------------------------------------
**If you installed Python 3.5 or later:** ``pyvenv-3.5`` (or whatever your version is) should already be working.

**If you are using Python 3.4:** Ubuntu 14.04 had a `broken pyvenv-3.4 package
<https://bugs.launchpad.net/ubuntu/+source/python3.4/+bug/1290847>`_,
so there is a small workaround to get it to work.::

    $ sudo apt-get install python3.4-venv

.. admonition:: Advanced users
  :class: tip

  If you prefer, you can use `Virtualenv <https://virtualenv.pypa.io/en/latest/installation.html>`_ instead.

1(c). PostgreSQL
--------------------------------------------------------------------------------
  *PostgreSQL is a database management system.*

As per the `PostgreSQL installation instructions <http://www.postgresql.org/download/linux/ubuntu/>`_::

    $ sudo apt-get install postgresql-9.4


2. Get the source code
================================================================================

There are two ways to get the source code: by using Git, or by downloading a release zip file. We encourage you to use Git. It'll be easier to keep up to date with Tabbycat and to deploy to a Heroku installation later. However, Git can be confusing for first-timers, so if you just want to get going, the tar.gz file will do fine.

Option 1: Clone the Git repository
--------------------------------------------------------------------------------
::

    $ git clone https://github.com/czlee/tabbycat.git

If you don't have Git, install it first using ``sudo apt-get install git``.

.. tip:: If you have a GitHub account, you might like to fork the repository
    first, to give yourself a little more freedom.

Option 2: Download a release package
--------------------------------------------------------------------------------

.. I'm not sure how to make this look right
.. parsed-literal::

    $ wget https\:\/\/github.com/czlee/tabbycat/archive/|vrelease|.tar.gz
    $ tar xf |vrelease|.tar.gz
    $ cd tabbycat-|release|


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

    $ pyvenv-3.4 venv

  (If you installed Python 3.5, use ``pyvenv-3.5``. If you're using Virtualenv, use ``virtualenv``.)

4. Run the ``activate`` script. This puts you "into" the virtual environment::

    $ source venv/bin/activate

5. Install Tabbycat's requirements into your virtual environment::

    $ pip install --upgrade pip
    $ pip install -r requirements_common.txt

6. Initialize the database and create a user account for yourself::

    $ dj makemigrations debate
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

Naturally, your database is currently empty, so proceed to :ref:`importing initial data <importing-initial-data>`.

Starting up an existing Tabbycat instance
================================================================================
To start your Tabbycat instance up again next time you use your computer::

    $ cd path/to/my/tabbycat
    $ source venv/bin/activate
    $ dj runserver
