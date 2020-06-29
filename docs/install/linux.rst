.. _install-linux:

===========================
Installing Locally on Linux
===========================

.. admonition:: Is this the best installation method for you?
  :class: attention

  In most cases, we recommend doing an :ref:`internet-based installation on Heroku <install-heroku>` instead. If you decide to do a local installation, be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

  If you just want to quickly set up a copy of Tabbycat to run locally on Linux, consider :ref:`installing using Docker<install-docker>`, which is a shorter process than the one below.

The instructions apply to both Linux, and :ref:`Linux on Windows <install-wsl>`.

Requisite technical background
==============================

You need to be familiar with command-line interfaces to get through this comfortably. While a background in the specific tools Tabbycat uses (Python, PostgreSQL, *etc.*) will make things easier, it's not necessary: we'll talk you through the rest.

.. admonition:: Advanced users
  :class: tip

  If you wish to use an SQL engine other that PostgreSQL, most of Tabbycat should work, but a few features rely on SQL functions that aren't supported by all engines. To configure Tabbycat to use a different engine, set the ``DATABASES`` `Django setting <https://docs.djangoproject.com/en/2.2/ref/settings/#databases>`_ accordingly.

Short version
=============
.. parsed-literal::

  curl -sL https\:\/\/deb.nodesource.com/setup_12.x | sudo -E bash -    # add Node.js source repository
  sudo apt install python3-dev python3-venv postgresql libpq-dev nodejs gcc g++ make
  git clone https\:\/\/github.com/TabbycatDebate/tabbycat.git
  cd tabbycat
  git checkout master
  sudo -u postgres createuser myusername --createdb --pwprompt    # skip if not first time
  createdb mydatabasename

Then create **settings/local.py** as described :ref:`below <local-settings-linux>`, then::

  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r ./config/requirements_core.txt
  npm install
  cd tabbycat
  dj migrate
  npm run build
  dj collectstatic
  dj createsuperuser
  dj runserver

1. Install dependencies
=======================
First, you need to install all of the software on which Tabbycat depends, if you don't already have it installed.

.. admonition:: Advanced users
  :class: tip

  These instructions are for Ubuntu, and are targeted at Ubuntu 18.04. If you have another distribution of Linux, we trust you'll know how to navigate the package manager for your distribution to install the dependencies.

.. _install-linux-python:

1(a). Python
------------
Tabbycat requires Python 3.6 or later.  You probably already have Python 3, but you'll also need the development package in order to install Psycopg2 later.  The ``venv`` module will come in handy too.  Install::

    $ sudo apt install python3-dev python3-venv

Check the version::

    $ python3 --version
    Python 3.6.2

.. warning:: Tabbycat does not support Python 2. You must use Python 3.6 or later.

1(b). PostgreSQL
----------------
  *PostgreSQL is a database management system.*

Install PostgreSQL using the  `PostgreSQL installation instructions here <http://www.postgresql.org/download/linux/ubuntu/>`_.

Normally, installing the latest stable version should be best, but if you're having issues, install the same version as the current `default version on Heroku <https://devcenter.heroku.com/articles/heroku-postgresql#version-support>`_, as that will be what is currently most commonly used with Tabbycat. If you're planning on pushing data between your local installation and a Heroku site, it's best to match the Heroku's current default version.

You'll also need the ``libpq-dev`` package in order to install Psycopg2 later::

    $ sudo apt install libpq-dev

.. _install-linux-nodejs:

1(c). Node.js/NPM
-----------------
  *Node.js is a JavaScript runtime.*

Tabbycat requires Node and its package manager to compile front-end dependencies. Install using:

.. parsed-literal::

  $ sudo apt install curl
  $ curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
  $ sudo apt install -y nodejs
  $ sudo ln -s /usr/bin/nodejs /usr/bin/node

1(d). Other development tools
-----------------------------
Some of the Python packages require GCC, G++ and Make in order to install::

    $ sudo apt install gcc g++ make

.. _install-linux-source-code:

2. Get the source code
======================

Choose either of the following two methods.

Method 1 (Git clone)
--------------------

If you have Git, life will be easier if you clone `our GitHub repository`_:

.. parsed-literal::

    $ git clone https\:\/\/github.com/TabbycatDebate/tabbycat.git
    $ git checkout master

(You can find out if you have Git using ``git --version``. If you don't, you can install it using ``sudo apt install git``.)

.. note:: The default branch is ``develop``, so you need to explicitly change the branch to ``master``, which is what the ``git checkout master`` line does.

.. admonition:: Advanced users
  :class: tip

  You might like to fork the repository first, to give yourself a little more freedom to make code changes on the fly (and potentially :ref:`contribute <contributing>` them to the project).

Method 2 (tarball)
------------------

If you don't want to use Git, simply download and extract:

.. parsed-literal::

    $ wget https\:\/\/github.com/TabbycatDebate/tabbycat/archive/|vrelease|.tar.gz
    $ tar xf |vrelease|.tar.gz
    $ cd tabbycat-|release|

3. Set up a new database
========================

.. hint:: You can skip step 1 if this is not your first installation. Every Tabbycat installation requires its own database, but they can use the same login role if you like.

a. Create a new user account with a password, replacing ``myusername`` with whatever name you prefer. If you don't know what username to pick, use ``tabbycat``. Grant this user the ability to create databases, since this'll make it easier to spin up new instances of Tabbycat in the future.

  ::

    $ sudo -u postgres createuser myusername --createdb --pwprompt

  .. tip:: If you'll be running multiple instances of Tabbycat, developing, or diving into the database yourself, you might find it convenient to set up client authentication so that you don't need to do all manual operations from ``sudo -u postgres``. See the `PostgreSQL documentation on client authentication <http://www.postgresql.org/docs/9.6/static/client-authentication.html>`_ for more information. For example, you could add a ``local all myusername md5`` line to the *pg_hba.conf* file, or you could define a mapping in *pg_ident.conf* and append the ``map=`` option to the ``local all all peer`` line in *pg_hba.conf*.

b. Create a new database, replacing ``mydatabasename`` with whatever name you prefer, probably the name of the tournament you're running::

    $ createdb mydatabasename


.. _install-linux-tabbycat:

4. Install Tabbycat
===================
Almost there!

a. Navigate to your Tabbycat directory::

    $ cd path/to/my/tabbycat/directory

.. _local-settings-linux:

b. Start a new virtual environment. We suggest the name ``venv``, though it can be any name you like:

  .. code:: bash

    $ python3 -m venv venv

c. Run the ``activate`` script. This puts you "into" the virtual environment::

    $ source venv/bin/activate

d. Install Tabbycat's requirements into your virtual environment::

    $ pip install --upgrade pip
    $ pip install -r ./config/requirements_core.txt
    $ npm install

e. Navigate to the **tabbycat/settings** sub folder and copy **local.example** to **local.py**. Find this part in your new **local.py**, and fill in the blanks as indicated:

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

f. Navigate to the **tabbycat** sub-directory, initialize the database, compile the assets, and create a user account for yourself::

    $ cd tabbycat
    $ dj migrate
    $ npm run build
    $ dj collectstatic
    $ dj createsuperuser

g. Start Tabbycat!

  ::

    $ dj runserver

  It should show something like this::

    serving on http://127.0.0.1:8000

h. Open your browser and go to the URL printed above. (In the above example, it's http://127.0.0.1:8000.) It should look something like the screenshot below. If it does, great! You've successfully installed Tabbycat.

  .. image:: images/tabbycat-bare-linux.png
      :alt: Bare Tabbycat installation

Naturally, your database is currently empty, so proceed to :ref:`importing initial data <importing-initial-data>`.

Starting up an existing Tabbycat instance
=========================================
To start your Tabbycat instance up again next time you use your computer::

    $ cd path/to/my/tabbycat/directory
    $ source venv/bin/activate
    $ dj runserver
