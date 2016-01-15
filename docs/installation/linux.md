Before you start, be sure to read our general information on [[local installations]] to help you understand what's going on.

## Requisite technical background

You need to be familiar with command-line interfaces to get through this comfortably. While a background in the specific tools (Python, *etc.*) we use will make things easier for you, it's not necessary: we'll talk you through the rest.

> <i>Advanced users: Tabbycat is a Django project, so can be installed in any manner that Django projects can normally be installed. For example, if you prefer some SQL system other than PostgreSQL, you can use it so long as it's Django-compatible. Just be aware that we might not have tried it.</i></td></tr></table>

## 1. Install dependencies
First, you need to install all of the software on which Tabbycat depends, if you don't already have it installed.

> <strong>These instructions are for Ubuntu.</strong> If you have another distribution of Linux, we trust you'll know how to navigate the package manager for your distribution to install the dependencies.</td></tr></table>

### 1(a). Python
You probably already have Python installed. Check:
``` bash
$ python --version
Python 2.7.6
```
You must have Python 2.7 installed. For example, `2.7.6` and `2.7.10` are fine, but `2.6.9` and `3.4.3` are not. If you don't, run `sudo apt-get install python`, or [download Python 2.7.10 from the Python website](https://www.python.org/downloads/release/python-2710/).

### 1(b). Virtualenv
> *Virtualenv allows you to create separate, isolated virtual Python environments, each with their own packages installed.*

If you have pip installed, the [recommended way](https://virtualenv.pypa.io/en/latest/installation.html) is to use it to install virtualenv:
``` bash
$ pip install virtualenv
```

If you don't have pip, you can install it using `sudo apt-get install python-pip`, then run the above command. If you don't want pip, you can also install virtualenv using `sudo apt-get install python-virtualenv`.

### 1(c). PostgreSQL
> *PostgreSQL is a database management system.*

As per the [PostgreSQL installation instructions](http://www.postgresql.org/download/linux/ubuntu/),
``` bash
$ sudo apt-get install postgresql-9.4
```

## 2. Get the source code

There are two ways to get the source code: by using Git, or by downloading a release zip file. We encourage you to use Git. It'll be easier to keep up to date with Tabbycat and to deploy to a Heroku installation later. However, Git can be confusing for first-timers, so if you just want to get going, the tar.gz file will do fine.

### Option 1: Clone the Git repository
``` bash
$ git clone https://github.com/czlee/tabbycat.git
```

If you don't have Git, install it first using `sudo apt-get install git`.

> <i>If you have a GitHub account, you might like to fork the repository first, to give yourself a little more freedom.</i></td></tr></table>

### Option 2: Download a release package
1. [**Follow this link** to see our latest release is](https://github.com/czlee/tabbycat/releases).
2. Replacing `0.7.1` with whatever the latest version number is (not code name):

   ``` bash
   $ wget https://github.com/czlee/tabbycat/archive/v0.7.1.tar.gz
   $ tar xf v0.7.1.tar.gz
   $ cd tabbycat-0.7.1
   ```

## 3. Set up a new database

> You can skip step 1 if this is not your first installation. Every Tabbycat installation requires its own database, but they can use the same login role if you like.</td></tr></table>

1. Create a new user account with a password, replacing `myusername` with whatever name you prefer. If you don't know what username to pick, use `tabbycat`.
   ``` bash
   $ sudo -u postgres createuser myusername --pwprompt
   ```

   > If you'll be running multiple instances of Tabbycat, developing, or diving into the database yourself, you might find it convenient to set up client authentication so that you don't need to do all manual operations from <code>sudo -u postgres</code>. See the <a href="http://www.postgresql.org/docs/9.4/static/client-authentication.html">PostgreSQL documentation on client authentication</a> for more information. For example, you could add a <code>local all myusername md5</code> line to the <code>pg_hba.conf</code> file, or you could define a mapping in <code>pg_ident.conf</code> and append the <code>map=</code> option to the <code>local all all peer</code> line. If you want your new PostgreSQL account to be able to create databases, add <code>--createdb</code> to the above command.</td></tr></table>

2. Create a new database, replacing `mydatabasename` with whatever name you prefer, probably the name of the tournament you're running.
   ``` bash
   $ sudo -u postgres createdb mydatabasename --owner myusername
   ```

## 4. Install Tabbycat
Almost there!

1. Navigate to your Tabbycat directory.
   ``` bash
   $ cd path/to/my/tabbycat
   ```

2. Copy **local_settings.example** to **local_settings.py**. Find this part in your new local_settings.py, and fill in the blanks as indicated:
   ``` python
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
   ```

3. Start a new virtual environment. We suggest the name `venv`, though it can be any name you like.
   ``` bash
   $ virtualenv venv
   ```

4. Run the `activate` script. This puts you "into" the virtual environment.
   ``` bash
   $ source venv/bin/activate
   ```

5. Install Tabbycat's requirements into your virtual environment
   ``` bash
   $ pip install --upgrade pip
   $ pip install -r requirements_common.txt
   ```

6. Initialize the database and create a user account for yourself.
   ``` bash
   $ dj makemigrations debate
   $ dj migrate
   $ dj createsuperuser
   ```

7. Start Tabbycat!
   ``` bash
   $ dj runserver
   ```

   It should show something like this:
   ```
   Performing system checks...

   System check identified no issues (0 silenced).
   August 21, 2015 - 10:40:42
   Django version 1.8.2, using settings 'settings'
   Starting development server at http://127.0.0.1:8000/
   Quit the server with CONTROL-C.
   ```

8. Open your browser and go to the URL printed above. (In the above example, it's http://127.0.0.1:8000/.) It should look something like this:

   ![Bare Tabbycat installation](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/tabbycat-bare-linux.png)

   If it does, great! You've successfully installed Tabbycat.

Naturally, your database is currently empty, so proceed to **[[importing initial data]]**.

## Starting up an existing Tabbycat instance
To start your Tabbycat instance up again next time you use your computer:
``` bash
$ cd path/to/my/tabbycat
$ source venv/bin/activate
$ dj runserver
```