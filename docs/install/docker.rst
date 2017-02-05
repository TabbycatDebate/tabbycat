.. _install-docker:

===============================
Installing Locally using Docker
===============================

Docker allows us to easily running a seperate operating system and collection of software. This means that we can bundle everything necessary to run Tabbycat into a single, isolated, 'virtual machine' rather than having users install all the needed components step-by-step. Once installed this virtual machine acts as a webserver and database that run Tabbycat, and can be started and stopped whenever you need to run Tabbycat.

1. Install Docker
=================

Docker offers a installer for Windows and OSX. Go to the relevant page linked below, download the *Stable Channel*, then open the file and follow the isntall prompts.

- `Docker for Mac download page <https://docs.docker.com/docker-for-mac/>`_.
- `Docker for Windows download page <https://docs.docker.com/docker-for-windows/>`_.

  .. note:: Docker requires Windows 10. Before or shortly after installing
    Docker will ask you to enable hypervisor and restart your PC. You must do this step.

- If you're on Linux `follow the instructions for your particular release here <https://docs.docker.com/engine/installation/linux/>`_.

2. Download Tabbycat
====================

1. `Go to the page for our latest release <https://github.com/czlee/tabbycat/releases/latest>`_.

2. Download the zip or tar.gz file.

3. Extract all files in it to a folder of your choice.

3. Run Tabbycat in Docker
=========================

1. Ensure docker app is open (there will be a whale icon in your menu/task bar) and that it says that docker is running.

2. Browse to the location where you extracted Tabbycat to, then open up the ``bin`` folder.

    - If on OSX, open ``osx_docker_start.command``
    - If on Windows, open ``windows_docker_start.bat``
    - If on Linux, open up a terminal in the Tabbycat folder (ie the folder containing ``README.md``) and run ``$ docker-compose up``

3. A terminal window should popup and bunch of text scroll by. If this is your first time running Docker it may take up to half an hour to download and setup the virtul machine.

4. Once the new text stops being added you should be able to go to a web and open up http://localhost:8000/ (Windows) or http://0.0.0.0:8000 (OSX/Linux) and see your new Tabbycat website.

  .. note:: If you want to reopen Tabbycat at a later time (say after restarting) repeat steps 1 through 3 here.
