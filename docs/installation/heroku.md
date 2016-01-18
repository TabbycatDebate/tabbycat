# Installing Tabbycat on Heroku

When running Tabbycat on the internet, we set it up on [Heroku](http://www.heroku.com/). The project is set up to be good to go on Heroku, and it works well for us, so if you'd like to run it online, we recommend that you do the same. Naturally, this requires you to [signup for a free Heroku account](https://signup.heroku.com/).

> *__Note__: You need to have at least a passing familiarity with command-line interfaces to get through this. We'll talk you through the rest.

> *__Advanced users__: Tabbycat is a Django project. As such, it can be installed on any web platform that supports Django, using any SQL system that Django supports. If you have some other means of running Django projects, there's no reason known to us why it wouldn't work, though of course different platforms may require different file structures.*

## Installation Instructions

We've tested these instructions successfully on Windows, Linux and Mac OS.

1. __Install Heroku Toolbelt__
    - If you don't already have it, go to [toolbelt.heroku.com](https://toolbelt.heroku.com/) and install the Heroku Toolbelt. To our knowledge, there's no way to install Tabbycat without Heroku Toolbelt, because you need it in order to initialize the database.
2. __Clone the Git repository__
    - Linux and OS X users should already have git installed; Windows users may need to [install it](http://git-scm.com/download/win)
    - Clone the Git repository to your computer. Open **Command Prompt** (Windows) or **Terminal** (Linux, Mac OS). Navigate to an appropriate directory on your computer using `cd` (creating directories using `mkdir` as appropriate), then run this command (without the `$` sign):

            $ git clone https://github.com/czlee/tabbycat.git

    - Then navigate to your new directory:

            $ cd tabbycat

    > *__Note__: If this is your second time creating a Tabbycat instance on Heroku from this computer, you don't need to clone the repository a second time. Just run ```git pull``` to update the code to the latest version, and press ahead to step 3: Deploy to Heroku.*

3. __Windows users: Install Python__

    - If you're using Windows, you need to install Python. Follow the instructions in (only!) part 1(a) of [our Windows instructions](windows.md) to do so. Unlike with local installations (which require Python 3.4), you can install any version from 2.7 onwards if you wish. The only script we'll be running is `deploy_heroku.py`, which is compatible with both Python 2 and Python 3.
    > *__Note__:If you're on Linux or OS X, you probably already have Python installed.*

3. __Deploy to Heroku__

    - When you first setup the Heroku toolbelt you need to login with your heroku account. To do so run this command and fill in the required details:

            $ heroku login

    - Now, run the script to deploy the app to Heroku. Replace `<yourappname>` with your preferred URL. Your website will be at `<yourname>.herokuapp.com`.

            $ python deploy_heroku.py <yourappname>

    - This script has other options that you might find useful. Run `python deploy_heroku.py --help` for details.<br><br>

    > __Note__: If you'd prefer to import tournament data locally and push the database to Heroku using [```heroku pg:push```](https://devcenter.heroku.com/articles/heroku-postgresql#pg-push), use the ```--no-init-db``` option to prevent ```deploy_heroku.py``` from running initial migrations on the database.*

    > __Note__: If this isn't your first tournament, the ```heroku``` Git remote might already be pointing to your first tournament. In this case, you should use the ```--git-remote &lt;new_remote_name&gt;``` option to get the script to create a new git remote for you, so you can use it in step 4.*

    - When this script finishes, it will open the app in your browser. It should look something like this:
    ![Tabbycat bare screenshot](/installation/images/tabbycat-bare.png)<br><br>

4. __Import tournament data__

    > *__Note__ this step is optional and there are other methods of [importing data](../use/importing-data). However the following method is most useful for large tournaments where manual entry would be tedious.*

    - In order to use the `import_tournament` command directly on the server, your data also needs to be on the server. The best way to get this data on to the server is to make a Git commit and `git push` it to the server.
    1. Place your CSV files in `data/yourtournamentname`, as described in [Importing initial data](../use/importing-data.md).
    2. Commit and push:

            $ git commit -am "Add data for <yourtournamentname>"
            $ git push heroku master

    > *__Note__: If you use ```--git-remote``` in step 3 to create your own Git remote, you should use that remote name instead of ```heroku``` in the last command above. You might like to create a new branch to keep this data off your master branch. If that sentence didn't make sense to you, ignore it.*

    - Then, run this command, replacing `<fields>` with your own names:


            $ heroku run dj importtournament <yourdatadirectoryname> --slug <slug> --name <Your Awesome Tournament> --short-name <Awesome>


## Heroku Addons

For Australs 2014, we found that the `hobby-dev` plan of [Heroku Postgres](https://elements.heroku.com/addons/heroku-postgresql) didn't allow for more than 10,000 database rows, so we upgraded to `hobby-basic`, which was enough (and costs a few dollars). At the end of that tournament, we had about 20,000 rows. For similar-sized tournaments (84 teams, 8 prelim rounds), you'll probably find your usage about the same, wheras small tournaments should fit within the 10,000 row limit easily.

If you're not sure, you can always start at `hobby-dev`&mdash;just be prepared to [upgrade](https://devcenter.heroku.com/articles/upgrade-heroku-postgres-with-pgbackups) during the tournament if you run close to capacity.

## Custom Domain Names

Your Heroku app will be available at *yourappname.herokuapp.com*. You may want it to be a subdomain of your tournament's website, like [tab.australasians2015.org](http://tab.australasians2015.org). Instructions for this are [in the Heroku documentation](https://devcenter.heroku.com/articles/custom-domains). Basically there are two things to do:

1. Add a DNS entry to your website, with record `CNAME`, name `tab` (or whatever you prefer) and target `yourappname.herokuapp.com`. You'll need to figure out how to do this with your tournament website hosting service (which is probably not Heroku).

2. Add a custom subdomain to Heroku, like this:

        $ heroku domains:add tab.yourwebsite.com