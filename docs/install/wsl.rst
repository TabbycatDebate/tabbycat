.. _install-wsl:

=====================================
Installing Locally on Bash on Windows
=====================================

.. admonition:: Is this the best install method for you?
  :class: attention

  In most cases, we recommend doing an :ref:`internet-based installation on Heroku <install-heroku>` instead. If you decide to do a local installation, be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

  If you just want to quickly set up a copy of Tabbycat to run locally on Windows, we recommend :ref:`installing using Docker<install-docker>`, which is much easier than the process below.

Requisite technical background
==============================

`Bash on Windows is in beta <https://msdn.microsoft.com/en-us/commandline/wsl/about>`_, so you should be confident with command-line interfaces, have at least some experience with Linux and, most importantly, **be willing to work with beta systems**. This means that Bash on Windows isn't yet fully stable and some features are incomplete. We've managed to get it going, but we haven't rigorously tested it, so if you're going to use this for a real tournament, you should either run an entire test tournament first or use a different installation method (like :ref:`Docker <install-docker>`).

If you're not already familiar with Bash on Windows, you should be willing to familiarise yourself with it, including potentially things not mentioned in these instructions. While a background in the specific tools (Python, *etc.*) we use will make things easier for you, it's not necessary: we'll talk you through the rest.

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a `Django <https://www.djangoproject.com/>`_ project, so can be installed in any manner that Django projects can normally be installed. For example, if you prefer some SQL system other than PostgreSQL, you can use it so long as it's Django-compatible. Just be aware that we haven't tried it.

Differences from the Linux installation
=======================================

For the most part, these instructions mirror those for doing local installations on Linux. The only difference is that, rather than installing PostgreSQL on Linux, you'll install **PostgreSQL for Windows**. The reason for this is that `PostgreSQL doesn't yet work on the Windows Subsystem for Linux <https://github.com/Microsoft/BashOnWindows/issues/61>`_. As of February 2017, there is a fix on the Windows Insider Preview Build, but it's still making its way to general availability.

This has a number of consequences:

1. You'll still install the PostgreSQL *client* on the Linux subsystem, using that to communicate with the server on Windows.
2. Because you won't install the PostgreSQL server, you need to install ``libpq-dev`` instead, in order for the ``psycopg2`` module to work.
3. These instructions will direct you to create the PostgreSQL role and database in **pgAdmin**, just like in the :ref:`Windows instructions <install-windows-database>`.

Short version
=============
First, install `PostgreSQL for Windows <https://www.postgresql.org/download/windows/>`_ (on Windows, not on the subsystem for Linux). Once you've set it up, create a new role and database as instructed in the Windows instructions in section :ref:`install-windows-database`. Then, in a Bash on Windows shell:

.. parsed-literal::

  curl -sL https\:\/\/deb.nodesource.com/setup_5.x | sudo -E bash -    # add Node.js source repository
  sudo apt-get install python3-dev python3-venv libpq-dev postgresql-client-9.6 nodejs

  # either
  wget https\:\/\/github.com/czlee/tabbycat/archive/|vrelease|.tar.gz
  tar xf |vrelease|.tar.gz
  cd tabbycat-|release|
  # or
  git clone https\:\/\/github.com/czlee/tabbycat.git
  git checkout |vrelease|                                         # or master

Then create local_settings.py as described in the :ref:`Linux instructions <local-settings-linux>`, then::

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

Follow these instructions:

- :ref:`install-linux-python` in the Linux instructions, on the Bash subsystem
- :ref:`install-windows-postgresql` in the Windows instructions (in Windows)
- :ref:`install-linux-nodejs` in the Linux instructions, on the Bash subsystem

2. Get the source code
======================

Follow section ":ref:`install-linux-source-code`" in the Linux instructions, on the Bash subsystem.

3. Set up a new database
========================

Follow section ":ref:`install-windows-database`" in the Windows instructions (in Windows).

4. Install Tabbycat
===================

Follow section ":ref:`install-linux-tabbycat`" in the Linux instructions, on the Bash subsystem.

Starting up an existing Tabbycat instance
=========================================
To start your Tabbycat instance up again next time you use your computer::

    $ cd /mnt/c/path/to/my/tabbycat/directory
    $ source venv/bin/activate
    $ cd tabbycat
    $ waitress-serve wsgi:application
