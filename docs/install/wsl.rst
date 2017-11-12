.. _install-wsl:

=================================================
Installing Locally on Windows Subsystem for Linux
=================================================

.. admonition:: Is this the best installation method for you?
  :class: attention

  In most cases, we recommend doing an :ref:`internet-based installation on Heroku <install-heroku>` instead. If you decide to do a local installation, be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

  If you just want to quickly set up a copy of Tabbycat to run locally on Windows, consider :ref:`installing using Docker<install-docker>`, which is a shorter process than the one below.

.. note::

  Windows Subsystem for Linux was taken out of beta in the `Windows 10 Fall Creators Update <https://blogs.windows.com/windowsexperience/2017/10/17/whats-new-windows-10-fall-creators-update/>`_, which was released in October 2017. On Windows 10 computers, we now recommend this local installation method over :ref:`installing it directly on Windows <install-windows>`.

Requisite technical background
==============================

It will help a lot if you have some experience with Linux, but mainly you need to be familiar with command-line interfaces, and you should be willing to install and work with the `Windows Subsystem for Linux <https://msdn.microsoft.com/en-us/commandline/wsl/about>`_. You might need to be prepared to familiarise yourself with aspects of WSL not covered in these instructions. While a background in the specific tools Tabbycat uses (Python, PostgreSQL, *etc.*) will make things easier, it's not necessary: we'll talk you through the rest.

You might need to `check that you have the Fall Creators Update (build 1709) first <https://support.microsoft.com/en-us/help/4028685/windows-10-get-the-fall-creators-update>`_.

Windows Subsystem for Linux is only available on Windows 10. If you have an older version of Windows, :ref:`install Tabbycat locally on Windows <install-windows>` instead.

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a `Django <https://www.djangoproject.com/>`_ project, so can be installed in any manner that Django projects can normally be installed. For example, if you prefer some SQL system other than PostgreSQL, you can use it so long as it's Django-compatible. Just be aware that we haven't tried it.

Differences from the Linux installation
=======================================

For the most part, these instructions mirror those for doing local installations on Linux. The only difference is that, rather than installing PostgreSQL on Linux, you'll install **PostgreSQL for Windows**.

The reason for this is that, when these instructions were first written, the `PostgreSQL server didn't work on the Windows Subsystem for Linux <https://github.com/Microsoft/BashOnWindows/issues/61>`_. A fix for this is reportedly in the Fall Creators Update, but we haven't tried it yet. (Of course, you're welcome to, and we'd love to hear from you if you succeed.)

This has a number of consequences:

1. You'll still install the PostgreSQL *client* on the Linux subsystem, using that to communicate with the server on Windows.
2. Because you won't install the PostgreSQL server, you need to install ``libpq-dev`` instead, in order for the ``psycopg2`` module to work.
3. These instructions will direct you to create the PostgreSQL role and database in **pgAdmin**, just like in the :ref:`Windows instructions <install-windows-database>`.

Short version
=============
First, install `PostgreSQL for Windows <https://www.postgresql.org/download/windows/>`_ (on Windows, not on the subsystem for Linux). Once you've set it up, create a new role and database as instructed in the Windows instructions in section :ref:`install-windows-database`. Then, in a Bash shell:

.. parsed-literal::

  curl -sL https\:\/\/deb.nodesource.com/setup_6.x | sudo -E bash -    # add Node.js source repository
  sudo apt-get install python3-dev python3-venv libpq-dev postgresql-client-9.6 nodejs

  # either
  wget https\:\/\/github.com/TabbycatDebate/tabbycat/archive/|vrelease|.tar.gz
  tar xf |vrelease|.tar.gz
  cd tabbycat-|release|
  # or
  git clone https\:\/\/github.com/TabbycatDebate/tabbycat.git
  git checkout |vrelease|                                         # or master

Then create local_settings.py as described in the :ref:`Linux instructions <local-settings-linux>`, then::

  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements_common.txt
  npm install
  dj migrate
  npm run gulp build
  dj collectstatic
  dj createsuperuser
  dj runserver

1. Install dependencies
=======================

If you don't already have it, `install the Windows Subsystem for Linux <https://msdn.microsoft.com/en-us/commandline/wsl/install-win10>`_.

Then, follow these instructions:

- :ref:`install-linux-python` in the Linux instructions, on the Linux subsystem
- :ref:`install-windows-postgresql` in the Windows instructions (in Windows)
- :ref:`install-linux-nodejs` in the Linux instructions, on the Linux subsystem

2. Get the source code
======================

Follow section ":ref:`install-linux-source-code`" in the Linux instructions, on the Linux subsystem.

.. attention::

  You should put the source code somewhere in your Windows file system, not your Linux file system. See `this page on the Microsoft Developers blog <https://blogs.msdn.microsoft.com/commandline/2016/11/17/do-not-change-linux-files-using-windows-apps-and-tools/>`_ for why.

3. Set up a new database
========================

Follow section ":ref:`install-windows-database`" in the Windows instructions (in Windows).

4. Install Tabbycat
===================

Follow section ":ref:`install-linux-tabbycat`" in the Linux instructions, on the Linux subsystem.

Starting up an existing Tabbycat instance
=========================================
To start your Tabbycat instance up again next time you use your computer::

    $ cd /mnt/c/path/to/my/tabbycat/directory
    $ source venv/bin/activate
    $ dj runserver
