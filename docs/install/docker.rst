.. _install-docker:

===============================
Installing Locally using Docker
===============================

.. admonition:: Is this the best install method for you?
  :class: attention

  In most cases, we recommend doing an :ref:`internet-based installation on Heroku <install-heroku>` instead. If you decide to do a local installation, be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

.. attention:: If you need an offline copy of Tabbycat, installing using Docker should be simpler and quicker than using the "Install Locally on…" instructions for your operating system. However if a Docker installation doesn't work as outlined below, it's harder to address what isn't working. If you encounter any problems with Docker, we recommend using the "Install Locally on…" option as a fallback, but if you need to do so, `please also report the issue you're having on GitHub <https://github.com/TabbycatDebate/tabbycat/issues/new?labels=installation-docker&title=Docker%20installation%20problem&body=Please%20be%20sure%20to%20include%20your%20operating%20system%20and%20version,%20and%20please%20be%20as%20specific%20as%20you%20can%20about%20the%20problem%20you%20encountered%3A%0D%0D>`_ or :ref:`contact the developers <authors>`.

Docker is an application that makes it very easy to load and run a specific collection of software. It allows us to bundle everything necessary to run Tabbycat into a single package rather than have users install everything needed step-by-step. Once set up, Docker will allow you to start and stop a webserver (that in turn runs Tabbycat) on your computer whenever you want and without the need for internet access.


1. Download Tabbycat
====================

1. `Go to the page for our latest release <https://github.com/TabbycatDebate/tabbycat/releases/latest>`_.

2. Download the zip or tar.gz file.

3. Extract all files in it to a folder of your choice.


2. Install Docker
=================

Install **Docker Desktop** for your operating system from the `Docker website <https://www.docker.com/products/docker-desktop>`_.

Notes for specific operating systems:

- **Windows users** will be asked to enable Hyper-V Windows Features or WSL 2 Features while installing Docker. Please do so and restart as asked. If you encounter any problems, our documentation might be outdated—check Docker's documentation `for Windows 10 Pro/Enterprise/Education <https://docs.docker.com/docker-for-windows/install/>`_ or `for Windows 10 Home <https://docs.docker.com/docker-for-windows/install-windows-home/>`_.
- **Linux users** will be directed to install `Docker Engine <https://hub.docker.com/search?q=&type=edition&offering=community&operating_system=linux>`_ instead.

3. Run Tabbycat in Docker
=========================

.. rst-class:: spaced-list

1. Ensure that Docker application is open (there should be a whale icon in your menu/task bar) and that it says that Docker is running.

2. Browse to the location where you extracted Tabbycat to. Open up the **bin** folder there. Within that folder:

    - If you're on macOS, press the Control key, click the icon for **osx_docker_start.command**, then choose Open from the shortcut menu.
    - If you're on Windows, open **windows_docker_start.bat**.
    - If you're on Linux, open up a terminal in the Tabbycat folder (*i.e.* the folder containing ``README.md``) and run ``docker-compose up``.

3. A terminal window should pop up and lots of text should scroll by. If this is your first time running Docker, it may take a while (30 minutes or more) to download the virtual machine. The last few lines will say something like:

  .. code-block:: none

    web_1  | Django version 2.2.13, using settings 'settings'
    web_1  | Starting ASGI/Channels version 2.2.0 development server at http://0.0.0.0:8000/
    web_1  | Quit the server with CONTROL-C.

4. Open up http://localhost:8000/ (Windows) or http://0.0.0.0:8000/ (macOS/Linux) in a browser of your choice!

.. note:: If you want to reopen Tabbycat at a later time (say after restarting), just repeat the steps in this section.
