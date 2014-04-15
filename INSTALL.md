Installation Instructions
-------------------------


1. You will need to have the following packages installed if you don't
   already have them:

         $ sudo apt-get install libpq-dev python-dev python-virtualenv

      If you're expecting the PostgreSQL database to be on your computer,
   don't forget you'll need the server as well as the client:

         $ sudo apt-get install postgresql

2. Create virtualenv named 'env' in root directory:

         $ virtualenv env

3. Source activation script (do this whenever you want to do work
   from the shell):

         $ source bin/activate

4. Install requirements:

         $ pip install -r requirements.txt

      This requires network access and can take a while to complete.

5. Copy ```config/local_settings.py.example``` to ```config/local_settings.py```
   and edit to match your local settings.


You should only need to do this once. Once you've done the installation,
you should never need to set up the virtual environment again - just run

      $ source bin/activate

...from this directory whenever you want to run anything (including run the
Django development server) from the shell.

While in the root directory the development server can be started using:

      $ python src/australs/manage.py runserver

On your first-run, you'll need to create the relevant database tables and relations using:

      $ python src/australs/manage.py syncdb

As well as setup the database migrations using [South](http://south.aeracode.org) as follows:

      $ python src/australs/manage.py migrate
