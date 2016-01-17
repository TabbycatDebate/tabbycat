.. _install-osx:

==========================
Installing locally on OS X
==========================

Before you start, be sure to read our general information on [[local installations]] to help you understand what's going on.

Requisite technical knowledge
=======================================================================

You need to be familiar with command-line interfaces to get through this comfortably. While a background in the specific tools (Python, *etc.*) we use will make things easier for you, it's not necessary: we'll talk you through the rest. You just need to be prepared to bear with us. It'll take a while the first time, but it gets easier after that.

Every line in the instructions that begins with `$` is a command that you need to run in a **Terminal**, but without the `$`: that sign is a convention used in instructions to make it clear that it is a command you need to run.

> <i>Advanced users: Tabbycat is a Django project, so can be installed in any manner that Django projects can normally be installed. For example, if you prefer some SQL system other than PostgreSQL, you can use it so long as it's Django-compatible. Just be aware that we might not have tried it.</i></td></tr></table>

1. Install dependencies
=======================================================================

In order to use Tabbycat, you must have Python 2.7, pip, virtualenv, Git and PostgresQL already installed on your machine. See the following for install instructions:

* [How to set up Git](https://help.github.com/articles/set-up-git) (all platforms)
* [How to install Python, pip, and virtualenv on OS X](http://docs.python-guide.org/en/latest/starting/install/osx/)
* [How to setup PostgreSQL on OS X](http://marcinkubala.wordpress.com/2013/11/11/postgresql-on-os-x-mavericks/)

> <strong>Note:</strong> Tabbycat requires Python 2.7, not 2.6 or any 3.x. We don't currently have plans to migrate to Python 3.</td></tr></table>

Installing
=======================================================================
1. Install the dependencies above.

2. Clone the repository:

        $ git clone https://github.com/czlee/tabbycat.git

3. Create a virtualenv in the project's root directory:

        $ virtualenv venv

4. Activate the virtualenv. Note that you'll need to activate the venv this way **each time** you want to run the project.

        $ source venv/bin/activate

5. Upgrade to the latest version of the pip installer:

        $ pip install --upgrade pip

6. Install the project's requirements. Note this requires an internet connection and can take some time:

        $ pip install -r requirements_common.txt

   *Known issues with requirements installation:*

    1. If on OS X 10.9+ or using XCode 5.1+, installing `psycopg2` may fail. In that case, run the following:

            $ ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install -r requirements_common.txt

7. If you like, you can do steps 7 and 8 in a new shell while the installation in step 6 is in progress.

   If you haven't already got one, create a blank database.

        $ createdb YOUR_DATABASE_NAME

   (If you've created a separate PostgresQL account for the database, you might precede this with `PGUSER=<username>` or use `-U <username>` option.)

8. Copy ```local_settings.example``` to ```local_settings.py``` and edit the settings in the `DATABASES` dictionary to match your database setup and the details of your blank database.  You most likely need to set `'NAME'`, `'USER'` and `'PASSWORD'`, to `YOUR_DATABASE_NAME`, your PostgresQL username and password respectively.

9. Sync and migrate the database:

        $ dj makemigrations debate
        $ dj migrate
        $ dj createsuperuser

   It's okay if the last line fails because something "already exists".

10. Start the local server using:

        $ dj runserver

11. Open the site up by visiting [127.0.0.1:8000](http://127.0.0.1:8000/)

Naturally, your database is probably currently empty, so proceed to [[importing initial data]].

Starting up the server the next time
-------------------------------------------------------------------------
To resume running the server at a later date, change to the Tabbycat directory and repeat steps 3 and 10, that is:

        $ cd [wherever your tabbycat directory is]/tabbycat
        $ source venv/bin/activate
        $ dj runserver