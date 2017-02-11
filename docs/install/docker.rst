.. _install-docker:

===============================
Installing Locally using Docker
===============================

.. admonition:: Is this the best install method for you?
  :class: attention

  In most cases, we recommend doing an :ref:`internet-based installation on Heroku <install-heroku>` instead. If you decide to do a local installation, be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

Docker is an application that makes it very easy to load and run a specific collection of software. It allows us to bundle everything necessary to run Tabbycat into a single 'virtual machine' rather than have users install everything needed step-by-step. Once set up, Docker will allow you to start and stop a webserver (that in turn runs Tabbycat) whenever you need.

1. Install Docker
=================

**Mac OS X, Linux and Windows 10 Pro/Enterprise/Education users:**

- Install **Docker** from the `Docker downloads page <https://www.docker.com/products/overview>`_.

**Windows 7, Windows 8 and Windows 10 Home users:**

- Install **Docker Toolbox** from the `Docker Toolbox downloads page <https://www.docker.com/products/docker-toolbox>`_.

.. note:: Before or shortly after installing Docker may ask you to enable hypervisor and restart your PC. You must do this step.

.. tip:: Not sure which edition of Windows you have? Click Start, search for "System", and open the Control Panel item "System".

2. Download Tabbycat
====================

1. `Go to the page for our latest release <https://github.com/czlee/tabbycat/releases/latest>`_.

2. Download the zip or tar.gz file.

3. Extract all files in it to a folder of your choice.

3. Run Tabbycat in Docker
=========================

If using Docker
---------------

*These instructions apply if you installed Docker, i.e., if you are using Mac OS X, Linux or Windows Pro/Enterprise/Education.*

1. Ensure that Docker application is open (there should be a whale icon in your menu/task bar) and that it says that Docker is running.

2. Browse to the location where you extracted Tabbycat to and then open up the **bin** folder there. Within that folder:

    - If you're on OS X, open **osx_docker_start.command**.
    - If you're on Windows, open **windows_docker_start.bat**.
    - If you're on Linux, open up a terminal in the Tabbycat folder (*i.e.* the folder containing ``README.md``) and run ``docker-compose up``.

3. A terminal window should popup and bunch of text scroll by. If this is your first time running Docker it may take up to half an hour to download and set up the virtual machine.

4. Once the new text has stopped scrolling for a little while it should automatically open up the Tabbycat site in your default browser. If this doesn't happen open up http://localhost:8000/ (Windows) or http://0.0.0.0:8000 (OSX/Linux) yourself.

  .. note:: If you want to reopen Tabbycat at a later time (say after restarting) repeat steps 1 through 3 under 'Run Tabbycat in Docker'.

If using Docker Toolbox
-----------------------

*These instructions apply if you installed Docker Toolbox, i.e., if you are using Windows 7, Windows 8 or Windows 10 Home.*

1. Start the **Docker Quickstart Terminal**.

2. Run the command ``docker-machine ip``. Take note of the IP address it shows, for example::

    $ docker-machine ip
    192.168.99.100

3. Navigate to the Tabbycat folder (*i.e.* the folder containing ``README.md``) and run ``docker-compose up``.

4. Open a browser and go to http://192.168.99.100:8000/, replacing "192.168.99.100" with whatever IP address was shown in step 2.

5. Once you're done and want to stop the Tabbycat server, press Ctrl+C, wait until the next prompt appears, and then run ``docker-machine stop``.
