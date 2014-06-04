# Tabbycat

Tabbycat is a draw tabulation system for 3 vs 3 debating tournaments. It was used at Auckland Australs 2010, [Victoria Australs 2012](http://australs2012.com) and will be used at [Otago Australs 2014](http://australs2014.com).

If you're interested in using, developing or otherwise following this software,
[join our Facebook group](https://www.facebook.com/groups/tabbycat.debate/).

## Features

- Enter data from multiple computers simultaneously
- Easily deployable to [Heroku](https://www.heroku.com) for a super fast setup
- Automated adjudicator allocations based on adjudicator ranking, room importance, and conflicts
- A drag and drop interface for adjudicator allocation that displays templates on the fly
- Responsive templates designed for large screens, laptops, tablets, and phones
- Optional online ballot submission
- Optional online post-tournament tab display

## Installing Tabby Cat

#### Assisted Setup

If you want to run a tournament with Tabby Cat but are not able to set it up, get in touch with [Philip](http://www.google.com/recaptcha/mailhide/d?k=01aItEbHtwnn1PzIPGGM9W8A==&c=XWljk2iGokfhziV2Rt4OiKA5uab1vCrnxwXcPUsWgnM=) and he can setup a private and online copy of the software for your use.

#### Setup on Linux or OS X

1. The project depends on having Python (2.6+), pip, virtualenv, git, postgreSQL, and a blank postgreSQL database setup on your local machine. See the following for install instructions:

    - [How to setup Git](https://help.github.com/articles/set-up-git)
    - [How to install Python, pip, and virtualenv on Linux](http://docs.python-guide.org/en/latest/starting/install/linux/)
    - [How to install Python, pip, and virtualenv on OS X](http://docs.python-guide.org/en/latest/starting/install/osx/)
    - [How to setup PostgreSQL on Linux](https://wiki.postgresql.org/wiki/Detailed_installation_guides#Any_UNIX-Like_Platform)
    - [How to setup PostgreSQL on OS X](http://marcinkubala.wordpress.com/2013/11/11/postgresql-on-os-x-mavericks/)

2. Once these dependencies are installed, download/clone/fork the repo and create a virtualenv in the project's root directory:

        $ virtualenv venv

3. Activate the virtualenv. Note that you'll need to activate the venv this way **each time** you want to run the project.

        $ source venv/bin/activate

3. Install the project's requirements. Note this requires an internet connection and can take some time:

        $ pip install -r requirements.txt

4. If on OS X 10.9+ or using XCode 5.1+, note that installing psycopg2 may fail. In which case run the following:

        $ ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install -r requirements.txt

5. Rename ```local_settings.example``` to ```local_settings.py``` and edit the settings on lines 20-29 to match your database setup and the details of your blank database.

6. Sync and migrate the database:

        $ python manage.py syncdb
        $ python manage.py schemamigration debate --initial
        $ python manage.py migrate debate

7. Start the local server using:

        $ foreman start

8. Open the site up by visiting [http://0.0.0.0:5000/](http://0.0.0.0:5000/)

Note that to resume running the server at a later date, you will need change to the project's directory and repeat **step 2** and **step 7** each time.

#### Deploy to Heroku

1. These commands can be used to deploy to Heroku, provided you have setup the [Heroku Toolbelt](https://devcenter.heroku.com/articles/getting-started-with-python#local-workstation-setup). Note that you can skip the local setup if you are just going to be running the tournament online.

        $ heroku create
        $ heroku ps:scale web=1
        $ heroku config:set HEROKU=1
        $ git push heroku master
        $ heroku run python manage.py syncdb
        $ heroku run python manage.py migrate
        $ heroku addons:add pgbackups
        $ heroku open

## Setting up a Tournament

#### Setting up a Tournament Manually

1. Open up your the admin area of your site by going to the local/heroku URL with /admin/ on the end, ie [*http://0.0.0.0:5000/admin/*](http://0.0.0.0:5000/admin/). 2. Then click **Debate** in the sidebar.
3. Create a new Tournament object, and input all of its rounds
4. Create the Venues
5. Create the Institutions
6. Create the Teams, and input their speakers
7. Create the Adjudicators, and input their conflicts

#### Setting up a Tournament Automatically (On a Local Install)

1. Copy and rename the ```data/dummy``` folder
2. See the csv files in the new folder, and add/replace the data as per your tournament. Note that the institutions (ie first row) in the ```speakers.csv``` and ```adjudicators.csv``` files must match the institutions in the second row of the ```institutions.csv``` file. And that all csv files must end with a blank line.
3. Use this command, replacing 'dummy' with your new folder's name:

        $ ./manage.py import_tournament dummy

#### Setting up a Tournament Automatically (On Heroku)

At present the ```import_tournament``` script does not work on Heroku. For now, if you want to automate the import process, do as follows:

1. Import and setup your tournament as per **Setting up a Tournament Automatically (On a Local Install)**

2. Deploy to heroku as per **Deploy to Heroku**, but skip running the lines with ```manage.py``` in them

3. Find the name of your heroku database (it will look something like ```HEROKU_POSTGRESQL_NAVY_URL```) using:

        $ heroku pg:psql

3. Use [```pg:push```](https://devcenter.heroku.com/articles/heroku-postgresql#pg-push) to copy your local database to Heroku. Note that your ```APP_NAME``` is the subdomain of your app at its heroku url.

        $ heroku pg:push LOCAL_DATABASE_NAME HEROKU_DATABASE_NAME --app APP_NAME

## Running a Tournament

#### Initial Configuration

1. After importing all your data, log into the site as an admin, and view the tournament configuration page. Adjust the speaker ranges and interface options to your liking.
2. Go to the /admin/ area to add any users that should have access to data-entry functions, but not the main tab backend. These should have *Active* and *Staff status* ticked.

#### In the Briefing

Some things you should probably mention in the briefing if using the online submissions feature:

- Adjudicators must fill out ballots completely, including motions and venues - they are entered into the system.
- There is a static URL for each person's ballots and feedback forms. It can be bookmarked, or the page can refreshed after each round.
- If people submit a result or feedback online, they should indicate that they have done so on the paper copy of their ballot.

#### Running a Round

1. Each round of the tournament has a number in the top right of the menu
2. For each round, you need to confirm the Venues, Teams, Adjudicators, and Participants are all available using the options in this menu.
3. The draw can then be generated on the Draw page
4. If using the public draw function, use the *Release to Public* button to publicly display the draw page.
5. Enter the motions for each round in the Motions page if you'd like information about motion selection and win rates.
6. Enter debate results and feedback as they come in (and/or allow online entry of results and feedback).
7. Both results and feedback entered in the tab room or online need to be confirmed before the results are counted.
8. When ready to advance to the next round, go to the Tournament section in the Django /admin/ area, select the current tournament, and increment the *Current Round*.

#### Wrapping Up

1. Tabs can be released using the *Tab released* option under configuration. Note that you probably want to turn off the *Public ballots*, *Public feedback*, *Feedback progress*, and *Public draw* options at this stage.

## Licensing and Development

We haven't released this under an open-source licence (so there is no formal general right to use this software), but if you're running a debating tournament, you're welcome to use it. It'd be nice if you could please let us know that you're doing so, and let us know how it went. [Our Facebook group](https://www.facebook.com/groups/tabbycat.debate/) is a great place to start. We're happy to help if you have any questions (contact below), though obviously we provide no warranty and disclaim all legal liability. Pull requests are encouraged.

Tabbycat was authored by Qi-Shan Lim for Auckland Australs 2010. Current active developers are Philip Belesky and Chuan-Zheng Lee. If you're interested in helping out, we'd love to have you. [Join our Facebook group](https://www.facebook.com/groups/tabbycat.debate/) and contact us as below.

If you need to contact one of us directly, contact Chuan-Zheng. I shouldn't be too hard to find, but the easiest thing to do is check out the repository and find my e-mail address in the commit history. Or message me on Facebook (czlee) or Twitter (@czlee11).



