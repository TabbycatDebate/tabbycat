.. _install-wsl:

============================================
Installing Locally on Linux on Windows (WSL)
============================================

.. admonition:: Is this the best installation method for you?
  :class: attention

  In most cases, we recommend doing an :ref:`internet-based installation on Heroku <install-heroku>` instead. If you decide to do a local installation, be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

  If you just want to quickly set up a copy of Tabbycat to run locally on Windows, consider :ref:`installing using Docker<install-docker>`, which is a shorter process than the one below.

  Windows Subsystem for Linux is only available on Windows 10. If you have an older version of Windows, :ref:`install Tabbycat locally on Windows <install-windows>` instead.

.. note::

  Windows Subsystem for Linux (WSL) was taken out of beta in the `Windows 10 Fall Creators Update <https://blogs.windows.com/windowsexperience/2017/10/17/whats-new-windows-10-fall-creators-update/>`_, which was released in October 2017. On Windows 10 computers, we now recommend this local installation method over :ref:`installing it directly on Windows <install-windows>`.

Requisite technical background
==============================

It will help a lot if you have some experience with Linux, but mainly you need to be familiar with command-line interfaces, and you should be willing to install and work with the `Windows Subsystem for Linux <https://docs.microsoft.com/windows/wsl/about>`_. You might need to be prepared to familiarise yourself with aspects of WSL not covered in these instructions. While a background in the specific tools Tabbycat uses (Python, PostgreSQL, *etc.*) will make things easier, it's not necessary: we'll talk you through the rest.


A. Install Ubuntu on Windows
============================

*If you already have a Linux distribution installed on your PC, skip to* :ref:`part B <install-wsl-tabbycat>`.

First, `check that you have the Fall Creators Update (build 1709) <https://support.microsoft.com/en-us/help/4028685/windows-10-get-the-fall-creators-update>`_. If you don't, update Windows.

Then, install the Windows Subsystem for Linux. For most people, this involves the following:

1. Enable the Windows Subsystem for Linux feature, by finding **Turn Windows features on or off** on the Start Menu, then checking the box for **Windows Subsystem for Linux** and clicking **OK**. You'll be prompted to restart your computer to make the changes take effect.
   
  .. image:: images/wsl-feature.png

2. Install Ubuntu by finding it on the Microsoft Store. For your convenience, `here's a direct link to Ubuntu on the Microsoft Store <https://www.microsoft.com/store/p/ubuntu/9nblggh4msv6>`_.

3. Launch Ubuntu and follow the instructions. You'll be prompted to create a user account for your Ubuntu system.

Some more detailed instructions, including some troubleshooting, are `available on Microsoft's website <https://docs.microsoft.com/windows/wsl/about>`_.

.. admonition:: Advanced users
  :class: tip

  You can, of course, use any Linux distribution that Windows supports. We just suggest Ubuntu because it's the most well-known (and the one that we use).

.. _install-wsl-tabbycat:

B. Install Tabbycat
===================

You now have a Linux subsystem running on your computer, so head over to the :ref:`instructions to install Tabbycat locally on Linux <install-linux>` and follow those (in full).
