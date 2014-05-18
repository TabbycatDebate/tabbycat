# Tabbycat

Tabbycat is a draw tabulation system for 3 vs 3 debating tournaments.

## Features

- Easily deployable to [Heroku](https://www.heroku.com) for a super fast setup
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

3. Activate the virtualenv. Nnote you will need to activate the venv each time you want to run the project.

        $ source venv/bin/activate

3. Install the project's requirements. Note this requires an internet connection and can take a while:

        $ pip install -r requirements.txt

4. Rename ```local_settings.py.example``` to ```local_settings.py```
   and edit to match your database setup.

5. Sync and migrate the database:

        $ python manage.py syncdb
        $ python manage.py migrate

6. Run using:

        $ foreman start

#### Deploy to Heroku

These commands can be used to deploy to Heroku, provided you have setup the [Heroku Toolbelt](https://devcenter.heroku.com/articles/getting-started-with-python#local-workstation-setup). Note that you can skip the local setup if you are just running on Heroku.

    $ heroku create
    $ heroku ps:scale web=1
    $ heroku config:set HEROKU=1
    $ git push heroku master
    $ heroku run python manage.py syncdb
    $ heroku run python manage.py migrate
    $ heroku open

#### Preparing a Tournament

1. Copy and rename the ```data/dummy``` folder
2. See the csv files in the new folder, and add/replace the data as per your tournament. Note that the institutions (ie first row) in the ```speakers.csv``` and ```adjudicators.csv``` files must match the institutions in the second row of the ```institutions.csv``` file. And that all csv files must end with a blank line.

#### Importing a Tournament

1. Use this command, replacing 'dummy' with your new folder's name:

        $ ./manage.py import_tournament dummy

#### Directing a Tournament

1. Each round of the tournament has a number in the top right of the menu
2. For each round, you need to confirm the Venues, Teams, Adjudicators, and Participants are all available using the options in this menu.
3.

## Developers and Development

Tabbycat was authored by Qi-Shan Lim for Auckland Australs 2010, was also used at [Victoria Australs 2012](http://australs2012.com), and will be used at [Otago Australs 2014](http://australs2014.com).

We haven't released this under an open-source licence (so there is no formal general right to use this software), but if you're running a debating tournament, you're welcome to use it. It'd be nice if you could please let us know that you're doing so, and let us know how it went. We're happy to help if you have any questions (contact below), though obviously we provide no warranty and disclaim all legal liability. Pull requests are encouraged.

Contact Chuan-Zheng Lee with any questions. I shouldn't be too hard to find, but the easiest thing to do is check out the repository and find my e-mail address in the commit history. Or message me on Facebook (czlee) or Twitter (@czlee11). If you're interested in using, developing or otherwise following this software,
[join our Facebook group](https://www.facebook.com/groups/tabbycat.debate/).




