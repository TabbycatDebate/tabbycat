# Tabbycat

Tabbycat is a draw tabulation system for 3 vs 3 debating tournaments.

## Features

- Enter data from multiple computers simultaneously
- Easily deployable to [Heroku](https://www.heroku.com) for a super fast setup
- Automated adjudicator allocations based on adjudicator ranking, room importance, and conflicts
- A drag and drop interface for adjudicator allocation that displays templates on the fly
- Responsive templates designed for large screens, laptops, tablets, and phones
- Optional online ballot submission
- Optional online post-tournament tab display

## Demo Page

*TODO*

## Screenshots

*TODO*

## Installation Instructions

#### Setup on Linux or OS X

1. Install Python, pip, and virtualenv following either [this guide (Linux)](http://docs.python-guide.org/en/latest/starting/install/linux/) or [this guide (OS X)](http://docs.python-guide.org/en/latest/starting/install/osx/). You will also need Git installed along with a database engine of your choice.

2. Create a virtualenv in the project's root directory:

        $ virtualenv venv

3. Activate the virtualenv. Note that you'll need to activate the venv each time you want to run the project.

        $ source venv/bin/activate

3. Install the project's requirements. Note this requires an internet connection and can take a while:

        $ pip install -r requirements.txt

4. Rename ```local_settings.example``` to ```local_settings.py```
   and edit to match your database setup.

5. Sync and migrate the database:

        $ python manage.py syncdb
        $ python manage.py migrate

6. Run using:

        $ foreman start

Once it's installed, the next time you want to run the project you just need to run

        $ source venv/bin/activate

before you start.

#### Deploy to Heroku

These commands can be used to deploy to Heroku, provided you have setup the [Heroku Toolbelt](https://devcenter.heroku.com/articles/getting-started-with-python#local-workstation-setup). Note that you can skip the local setup if you are just running on Heroku.

    $ heroku create
    $ heroku ps:scale web=1
    $ heroku config:set HEROKU=1
    $ git push heroku master
    $ heroku run python manage.py syncdb
    $ heroku run python manage.py migrate
    $ heroku open

#### Preparing a Tournament (Manual Data Entry)

1. Go to <your url>/admin/
2. Create a new Tournament object (and input the rounds)
3. Proceed to create Venues, Institutions, Teams (which also allows you to add speakers), and Adjudicators

#### Importing a Tournament Locally (Data Import)

1. Copy and rename the ```data/dummy``` folder
2. See the csv files in the new folder, and add/replace the data as per your tournament. Note that the institutions (ie first row) in the ```speakers.csv``` and ```adjudicators.csv``` files must match the institutions in the second row of the ```institutions.csv``` file. And that all csv files must end with a blank line.
3. Use this command, replacing 'dummy' with your new folder's name:

        $ ./manage.py import_tournament dummy

### Importing a Tournament on Heroku

At present the ```import_tournament``` script does not work on Heroku. For now:

1. Import the data on a local install

        $ ./manage.py import_tournament dummy

2. Add the backups plugin to Heroku

        $ heroku addons:add pgbackups

3. Make a copy of your local datatabase (replacing 'your_db_name') in the below:

        $ pg_dump -Fc --no-acl --no-owner -h localhost your_db_name > your_db_name

4. Upload the dump file to a web server somewhere

5. Restore the local dump to Heroku, replacing the URL with a link to your dump file

        $ heroku pgbackups:restore DATABASE 'https://s3.amazonaws.com/me/items/3H0q/mydb.dump'

#### Directing a Tournament

###### Initial Setup

1. First, view the tournament configuration page and adjust the speaker ranges and interface options.
2. Go to the /admin/ page to add any users that should have access to data-entry functions, but not the main tab backend. These should have *Active* and *Staff status* ticked.

###### Round-by-Round

1. Each round of the tournament has a number in the top right of the menu
2. For each round, you need to confirm the Venues, Teams, Adjudicators, and Participants are all available using the options in this menu.
3. The draw can then be generated on the Draw page
4. If using the public draw function, set the round to be released in the Django admin backend
5. If you desire motion break downs, enter the motions for each round in the Motions page

###### Wrapping Up

1. Tabs can be released using the *Tab released* option under configuration. Note that you probably want to turn off *Public ballots*, *Public feedback*, *Feedback progress*, and *Public draw* at this stage.

## Developers and Development

Tabbycat was authored by Qi-Shan Lim for Auckland Australs 2010, was also used at [Victoria Australs 2012](http://australs2012.com), and will be used at [Otago Australs 2014](http://australs2014.com).

We haven't released this under an open-source licence (so there is no formal general right to use this software), but if you're running a debating tournament, you're welcome to use it. It'd be nice if you could please let us know that you're doing so, and let us know how it went. We're happy to help if you have any questions (contact below), though obviously we provide no warranty and disclaim all legal liability. Pull requests are encouraged.

Contact Chuan-Zheng Lee with any questions. I shouldn't be too hard to find, but the easiest thing to do is check out the repository and find my e-mail address in the commit history. Or message me on Facebook (czlee) or Twitter (@czlee11). If you're interested in using, developing or otherwise following this software,
[join our Facebook group](https://www.facebook.com/groups/tabbycat.debate/).




