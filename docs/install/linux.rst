.. _install-linux:

===========================
Installing Locally on Linux
===========================

.. admonition:: Is this the best install method for you?
  :class: attention

  In most cases, we recommend doing an :ref:`internet-based installation on Heroku <install-heroku>` instead. If you decide to do a local installation, be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

  If you just want to quickly set up a copy of Tabbycat to run locally on Linux, we recommend :ref:`installing using Docker<install-docker>`, which is much easier than the process below.


Requisite technical background
==============================

You need to be familiar with command-line interfaces to get through this comfortably. While a background in the specific tools (Python, *etc.*) we use will make things easier for you, it's not necessary: we'll talk you through the rest.

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a `Django <https://www.djangoproject.com/>`_ project, so can be installed in any manner that Django projects can normally be installed. For example, if you prefer some SQL system other than PostgreSQL, you can use it so long as it's Django-compatible. Just be aware that we haven't tried it.

Short version
=============
.. parsed-literal::

  curl -sL https\:\/\/deb.nodesource.com/setup_5.x | sudo -E bash -    # add Node.js source repository
  sudo apt-get install python3-dev python3-venv postgresql-9.6 postgresql-server-dev-9.6 nodejs

  # either
  wget https\:\/\/github.com/czlee/tabbycat/archive/|vrelease|.tar.gz
  tar xf |vrelease|.tar.gz
  cd tabbycat-|release|
  # or
  git clone https\:\/\/github.com/czlee/tabbycat.git
  git checkout |vrelease|                                         # or master

  sudo -u postgres createuser myusername --pwprompt           # skip if not first time
  sudo -u postgres createdb mydatabasename --owner myusername

Then create local_settings.py as described :ref:`below <local-settings-linux>`, then::

  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements_common.txt
  npm install
  cd tabbycat
  dj migrate
  dj collectstatic
  dj createsuperuser
  waitress-serve wsgi:application

1. Install dependencies
=======================
First, you need to install all of the software on which Tabbycat depends, if you don't already have it installed.

.. admonition:: Advanced users
  :class: tip

  These instructions are for Ubuntu 14.04 and higher. If you have another distribution of Linux, we trust you'll know how to navigate the package manager for your distribution to install the dependencies.

.. _install-linux-python:

1(a). Python
------------
Tabbycat requires Python 3.4 or later.  You probably already have Python 3.4, but you'll also need the development package in order to install Psycopg2 later.  The ``venv`` module will come in handy too.  Install::

    $ sudo apt-get install python3-dev python3-venv

Check the version::

    $ python3 --version
    Python 3.4.4

.. warning:: Tabbycat does not support Python 2. You must use Python 3.4 or later.

.. admonition:: Advanced users
  :class: tip

  If you prefer, you can use `Virtualenv <https://virtualenv.pypa.io/en/latest/installation.html>`_ instead of Python's built-in ``venv`` module.

1(b). PostgreSQL
----------------
  *PostgreSQL is a database management system.*

You'll need the *server-dev* package in order to install Psycopg2 later. As per the `PostgreSQL installation instructions <http://www.postgresql.org/download/linux/ubuntu/>`_::

    $ sudo apt-get install postgresql-9.6 postgresql-server-dev-9.6

If using Ubuntu <14.10 substitute "postgresql-9.3" for "postgresql-9.6" in the above commands.

.. _install-linux-nodejs:

1(c). Node.js/NPM
-----------------
  *Node.js is a JavaScript runtime.*

Tabbycat requires Node and its package manager to compile front-end dependencies. Install using:

.. parsed-literal::

  $ sudo apt-get install curl
  $ curl -sL https://deb.nodesource.com/setup_5.x | sudo -E bash -
  $ sudo apt-get install -y nodejs
  $ sudo ln -s /usr/bin/nodejs /usr/bin/node

.. _install-linux-source-code:

2. Get the source code
======================

Download and extract:

.. parsed-literal::

    $ wget https\:\/\/github.com/czlee/tabbycat/archive/|vrelease|.tar.gz
    $ tar xf |vrelease|.tar.gz
    $ cd tabbycat-|release|

If you've used Git before, you might prefer to clone `our GitHub repository`_ instead:

.. parsed-literal::

    $ git clone https\:\/\/github.com/czlee/tabbycat.git
    $ git checkout |vrelease|                              # or master

.. tip:: You might like to fork the repository first, to give yourself a little more freedom to make code changes on the fly (and potentially :ref:`contribute <contributing>` them to the project).

3. Set up a new database
========================

.. hint:: You can skip step 1 if this is not your first installation. Every Tabbycat installation requires its own database, but they can use the same login role if you like.

1. Create a new user account with a password, replacing ``myusername`` with whatever name you prefer. If you don't know what username to pick, use ``tabbycat``.

  ::

    $ sudo -u postgres createuser myusername --pwprompt

  .. tip:: If you'll be running multiple instances of Tabbycat, developing, or diving into the database yourself, you might find it convenient to set up client authentication so that you don't need to do all manual operations from ``sudo -u postgres``. See the `PostgreSQL documentation on client authentication <http://www.postgresql.org/docs/9.6/static/client-authentication.html>`_ for more information. For example, you could add a ``local all myusername md5`` line to the *pg_hba.conf* file, or you could define a mapping in *pg_ident.conf* and append the ``map=`` option to the ``local all all peer`` line in *pg_hba.conf*. If you want your new PostgreSQL account to be able to create databases, add ``--createdb`` to the above command.

2. Create a new database, replacing ``mydatabasename`` with whatever name you prefer, probably the name of the tournament you're running::

    $ sudo -u postgres createdb mydatabasename --owner myusername


.. _install-linux-tabbycat:

4. Install Tabbycat
===================
Almost there!

1. Navigate to your Tabbycat directory::

    $ cd path/to/my/tabbycat/directory

.. _local-settings-linux:

2. Start a new virtual environment. We suggest the name ``venv``, though it can be any name you like:

  .. code:: bash

    $ python3 -m venv venv

3. Run the ``activate`` script. This puts you "into" the virtual environment::

    $ source venv/bin/activate

4. Install Tabbycat's requirements into your virtual environment::

    $ pip install --upgrade pip
    $ pip install -r requirements_common.txt
    $ npm install

5. Navigate to the **tabbycat** sub folder and copy **local_settings.example** to **local_settings.py**. Find this part in your new local_settings.py, and fill in the blanks as indicated:

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

6. Navigate to the **tabbycat** sub-directory, initialize the database, compile the assets, and create a user account for yourself::

    $ cd tabbycat
    $ dj migrate
    $ dj collectstatic
    $ dj createsuperuser

7. Start Tabbycat!

  ::

    $ waitress-serve wsgi:application

  It should show something like this::

    serving on http://0.0.0.0:8080

8. Open your browser and go to the URL printed above. (In the above example, it's http://0.0.0.0:8080.) It should look something like the screenshot below. If it does, great! You've successfully installed Tabbycat.

  .. image:: images/tabbycat-bare-linux.png
      :alt: Bare Tabbycat installation

Naturally, your database is currently empty, so proceed to :ref:`importing initial data <importing-initial-data>`.

Starting up an existing Tabbycat instance
=========================================
To start your Tabbycat instance up again next time you use your computer::

    $ cd path/to/my/tabbycat/directory
    $ source venv/bin/activate
    $ cd tabbycat
    $ waitress-serve wsgi:application
