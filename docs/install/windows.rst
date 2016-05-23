.. _install-windows:

=============================
Installing Locally on Windows
=============================

Before you start, be sure to read our general information on :ref:`local installations <install-local>` to help you understand what's going on.

Requisite technical background
==============================

You need to be familiar with command-line interfaces to get through this comfortably. While a background in the specific tools (Python, *etc.*) we use will make things easier for you, it's not necessary: we'll talk you through the rest. You just need to be prepared to bear with us. It'll take a while the first time, but it gets easier after that.

In these instructions, we'll use **Windows PowerShell**, a command-line interface that comes with every installation of Windows (since XP). The easiest way to find it (on Windows 7 and later) is to search for it in your Start Menu. Every line in the instructions that begins with ``>`` is a command that you need to run in PowerShell, but without the ``>``: that sign is a convention used in instructions to make it clear that it is a command you need to run.

.. admonition:: Advanced users
  :class: tip

  Tabbycat is a `Django <https://www.djangoproject.com/>`_ project, so can be installed in any manner that Django projects can normally be installed. For example, if you prefer some SQL system other than PostgreSQL, you can use it so long as it's Django-compatible. Just be aware that we might not have tried it.

1. Install dependencies
=======================

First, you need to install all of the software on which Tabbycat depends, if you don't already have it installed.

.. _install-python-windows:

1(a). Python
------------
  *Python is a popular programming language, and the language in which the core of Tabbycat is coded.*

Download and install Python 3.5 (or later) from the `Python website <https://www.python.org/>`_.
In the installer, check the box to add Python to your PATH (see box below).

.. hint:: Which file should I download?

    - If you have 32-bit Windows, choose the "Windows x86 executable installer".
    - If you have 64-bit Windows (and not an Itanium processor), it's better to choose the "Windows x86-64 executable installer".
    - If you're not sure whether you have 32-bit or 64-bit Windows, consult "About your PC" or "System Properties" in your Start Menu.

.. attention:: **Please take note:** Just after you open the installer,
  **check the "Add Python 3.5 to PATH" box**:

  .. image:: images/python-windows-path.png

To check that Python is installed correctly, open Windows PowerShell, type ``python`` and press Enter. It should look something like this. If you installed the 32-bit version, it will say ``32 bit`` instead of ``64 bit``.

.. image:: images/python-windows-installed.png

(To exit Python, type ``exit()`` then press Enter.)

.. note:: **If you already have Python**, great! Some things to double-check:

  - You must have at least Python 3.4, though we recommend Python 3.5.
  - Your installation directory must not have any spaces in it.
  - If that doesn't work, note that the following must be part of your ``PATH`` environment variable: ``C:\Python35;C:\Python35\Scripts`` (or as appropriate for your installation directory). Follow `the instructions here <https://www.java.com/en/download/help/path.xml>`_ to add this to your path.

1(b). PostgreSQL
----------------
  *PostgreSQL is a database management system.*

Go to the `PostgreSQL downloads page <http://www.postgresql.org/download/windows/>`_, then follow the link through to EnterpriseDB to download and install the latest version of PostgreSQL.

.. tip:: Once PostgreSQL is installed, the PostgreSQL service will run on your computer whenever you are using it. You might prefer to configure it so that it only runs when you want to run Tabbycat. To do this, open "Services" in your Control Panel on Windows, find the PostgreSQL service, and change its startup type to "Manual". This will tell it not to start whenever you log in. Then, if you want to run the server (so you can use Tabbycat), you can do so from "Services" by selecting the PostgreSQL service and clicking "Start the service".

1(c). Git
---------
  *Git is a version control system.*

We won't use Git directly, but Node.js (which we install in the next step)
requires Git to work. So, install the latest version for Windows from the
`Git website <https://git-scm.com/downloads>`_.

.. admonition:: Advanced users
  :class: tip

  If you already have `GitHub Desktop <https://desktop.github.com/>`_ installed,
  you might think that this would be good enough. Unfortunately, it's
  not---GitHub Desktop installs a portable version of Git. Node.js, on the other
  hand, requires the ``git`` to be in the ``PATH``, so it can call it directly.
  The easiest (but not only) way to do this is just to install Git from the link
  above.

1(d). Node.js/NPM
-----------------
  *Node.js is a JavaScript runtime.*

Download and run the `node.js Windows Installer (.msi) <https://nodejs.org/en/download/>`_

2. Get the source code
======================

1. `Go to the page for our latest release <https://github.com/czlee/tabbycat/releases/latest>`_.
2. Download the zip file.
3. Extract all files in it to a folder of your choice.

.. admonition:: Advanced users
  :class: tip

  If you've used Git before, you might prefer to clone `our GitHub repository`_ instead. Don't forget to check out the |vrelease| tag or the master branch.

  Even better, you might like to fork the repository first, to give yourself a little more freedom to make code changes on the fly (and potentially :ref:`contribute <contributing>` them to the project).

3. Set up a new database
========================

.. hint:: You can skip steps 2 and 3 if this is not your first installation. Every Tabbycat installation requires its own database, but they can use the same login role if you like.

1. Open the **pgAdmin** tool, which you installed as part of installing PostgreSQL. In the object browser on the left, double-click the server marked "(localhost:5432)". Log in using the password you set during installation.

2. Right-click Login Roles, and click "New Login Role…"

  .. image:: images/pgadmin-new-login-role-menu.png

3. Fill in the New Login Role box as follows (everything not listed below can be left as-is):

   - In the **Properties** tab, in **Role Name**, choose a user account name.<br />(If you really don't know what to pick, use "tabbycat".)
   - In the **Definition** tab, choose a **Password** and type it in **Password (again)**.

   Then click OK. (Remember this user name and password, you'll need it later.)

4. Right-click Databases, and click "New Database…"

  .. image:: images/pgadmin-new-database-menu.png

5. Fill in the New Database box as follows (everything not listed below can be left as-is):

   - In the **Properties** tab, in **Name**, choose a database name (with no spaces in it).
   - In the **Properties** tab, in **Owner**, type the name of the login role you just created.

   Then click OK. (Remember the database name, you'll need it later.)

4. Install Tabbycat
===================

Almost there!

1. Open a Windows PowerShell. Navigate to the folder where you cloned/extracted Tabbycat. For example, if you installed it in ``C:\Users\myusername\Documents\GitHub\tabbycat``, then run::

    > Set-Location C:\Users\myusername\Documents\GitHub\tabbycat

2. Make a copy of **local_settings.example** and rename it to **local_settings.py**. Open your new local_settings.py. Find this part, and fill in the blanks (the empty quotation marks) as indicated:

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

3. Start a new virtual environment. We suggest the name `venv`, though it can be any name you like::

    > python -m venv venv

4. Run the `Activate.ps1` script. This puts you "into" the virtual environment::

    > .\venv\Scripts\Activate.ps1

  .. attention:: If you get an error message saying that the script isn't digitally signed, open a PowerShell with administrator privileges by right-clicking PowerShell in the Start meny and clicking "Run as administrator". Then run this command::

      > Set-ExecutionPolicy RemoteSigned

    Read the warning message, then type ``y`` to confirm. By default, the execution policy on Windows is ``Restricted``, which does not permit scripts like ``activate`` to be run. Changing it to ``RemoteSigned`` relaxes it to allow local scripts to be run without checking the signature.

5. Install Tabbycat's requirements.

  If you installed **32-bit Python**::

    > python -m pip install --upgrade pip
    > easy_install http://www.stickpeople.com/projects/python/win-psycopg/2.6.1/psycopg2-2.6.1.win32-py3.5.exe
    > pip install -r requirements_common.txt
    > npm install

  If you installed **64-bit Python**::

    > python -m pip install --upgrade pip
    > easy_install http://www.stickpeople.com/projects/python/win-psycopg/2.6.1/psycopg2-2.6.1.win-amd64-py3.5.exe
    > pip install -r requirements_common.txt
    > npm install

  If you're using a version of **Python other than 3.5**, replace the URL in the
  second line with the appropriate link from the
  `win-psycopg page <http://www.stickpeople.com/projects/python/win-psycopg/>`_.

  .. note:: The second line above is an extra step just for Windows. It installs the Windows version of ``psycopg2``, `win-psycopg <http://www.stickpeople.com/projects/python/win-psycopg/>`_, and must be done before ``pip install -r requirements_common.txt`` so that the latter doesn't try to install the Unix version.

  .. hint:: You might be wondering: I thought I already installed the requirements. Why am I installing more? And the answer is: Before, you were installing the requirements to create a Python virtual environment for Tabbycat to live in. Now, you're *in* the virtual environment, and you're installing everything required for *Tabbycat* to operate.

6. Initialize the database and create a user account for yourself::

    > dj migrate
    > dj collectstatic
    > dj createsuperuser

7. Start Tabbycat!

  ::

    > waitress-serve wsgi:application

  It should show something like this::

    serving on http://0.0.0.0:8080

8. Open your browser and go to the URL printed above. (In the above example, it's http://0.0.0.0:8080/.) It should look something like this:

  .. image:: images/tabbycat-bare-windows.png

  If it does, great! You've successfully installed Tabbycat.

Naturally, your database is currently empty, so proceed to :ref:`importing initial data <importing-initial-data>`.

Starting up an existing Tabbycat instance
=========================================

To start your Tabbycat instance up again next time you use your computer, open a PowerShell and::

    > Set-Location C:\Users\myusername\Documents\GitHub\tabbycat # or wherever your installation is
    > .\venv\Scripts\activate
    > waitress-serve wsgi:application
