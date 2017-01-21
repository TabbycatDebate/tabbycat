.. _backups:

=======
Backups
=======

The backup utility isn't part of Tabbycat. Heroku provides a very good backup
utility for all sites hosted on Heroku, and for Heroku-based Tabbycat sites,
we strongly recommend it.

You should **always** back up the database before deleting *any* data while in
the Edit Database area, because deleting data cannot be undone. It is also a
good idea to back up the database before doing anything in the Edit Database
area, unless you're very familiar and confident with editing the Tabbycat
database directly.

You may, as a matter of standard practice at large tournaments, wish to back up
the database twice per round: Once just after you've generated the draw and
allocated adjudicators, and once just after you've finished entering results.

Installations on Heroku
=======================

Heroku provides a utility to easily back up and restore the entire site
database.

If you don't have the Heroku CLI
--------------------------------
You can capture backups from the Heroku Dashboard:

1. Go to the `Heroku Dashboard <http://dashboard.heroku.com/>`_ and click
   on your app.
2. Under *Installed add-ons*, go to **Heroku Postgres**.
3. Scroll down, and click on the **Capture Backup** button.

You can't restore a backup without the Heroku Command Line Interface (CLI), so
if you end up needing your backup, you'll need to install the
`Heroku CLI <https://devcenter.heroku.com/articles/heroku-cli>`_, and then
follow the instructions below.

If you have the Heroku CLI
--------------------------

The best guide to backing up databases is the
`Heroku Dev Center's PGBackups guide <https://devcenter.heroku.com/articles/heroku-postgres-backups>`_.

To capture a backup::

    $ heroku pg:backups:capture

To restore a backup::

    $ heroku pg:backups:restore

If you have multiple Tabbycat sites, you'll need to specify which one by adding
``--app mytournamentname`` to the end of the command.

Local installations
===================

There are lots of ways to back up local PostgreSQL databases, but we'd suggest
using the
`pg_dump <https://www.postgresql.org/docs/current/static/app-pgdump.html>`_
and
`pg_restore <https://www.postgresql.org/docs/current/static/app-pgrestore.html>`_
commands.
