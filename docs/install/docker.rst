.. _install-docker:

===============================
Installing Locally using Docker
===============================

**Before you start:** Be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

Docker is an application that makes it very easy to load and run a specific collection of software. It allows us to bundle everything necessary to run Tabbycat into a single 'virtual machine' rather than have users install everything needed step-by-step. Once set up, Docker will allow you to start and stop a webserver (that in turn runs Tabbycat) whenever you need.

1. Install Docker
=================

Docker offers a standard installer for Windows and OS X. Go to the relevant page linked below, download the *Stable Channel* build, then open the file and follow the install prompts.

- `Docker for Mac download page <https://docs.docker.com/docker-for-mac/>`_.
- `Docker for Windows download page <https://docs.docker.com/docker-for-windows/>`_.

  .. note:: Docker requires Windows 10. Before or shortly after installing
    Docker will ask you to enable hypervisor and restart your PC. You must do this step.

- If you run Linux `follow the instructions for your particular release here <https://docs.docker.com/engine/installation/linux/>`_.

2. Download Tabbycat
====================

1. `Go to the page for our latest release <https://github.com/czlee/tabbycat/releases/latest>`_.

2. Download the zip or tar.gz file.

3. Extract all files in it to a folder of your choice.

3. Run Tabbycat in Docker
=========================

1. Ensure that Docker application is open (there should be a whale icon in your menu/task bar) and that it says that Docker is running.

2. Browse to the location where you extracted Tabbycat to and then open up the **bin** folder there. Within that folder:

    - If on OSX, open **osx_docker_start.command**
    - If on Windows, open **windows_docker_start.bat**
    - If on Linux, open up a terminal in the Tabbycat folder (ie the folder containing ``README.md``) and run ``$ docker-compose up``

3. A terminal window should popup and bunch of text scroll by. If this is your first time running Docker it may take up to half an hour to download and setup the virtul machine.

4. Once the new text has stopped scrolling for a little while it should automatically open up the Tabbycat site in your default browser. If this doesn't happen navigation to http://localhost:8000/ (On Windows) or http://0.0.0.0:8000 (On OSX/Linux) yourself.

  .. note:: If you want to reopen Tabbycat at a later time (say after restarting) repeat steps 1 through 3 under 'Run Tabbycat in Docker'.
