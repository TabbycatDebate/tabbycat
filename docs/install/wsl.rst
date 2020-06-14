.. _install-wsl:

============================================
Installing Locally on Linux on Windows (WSL)
============================================

.. admonition:: Is this the best installation method for you?
  :class: attention

  In most cases, we recommend doing an :ref:`internet-based installation on Heroku <install-heroku>` instead. If you decide to do a local installation, be sure to read our page on :ref:`local installations <install-local>` to help you understand what's going on, particularly this section: :ref:`install-decision`

  If you just want to quickly set up a copy of Tabbycat to run locally on Windows, consider :ref:`installing using Docker<install-docker>`, which is a shorter process than the one below.

  Windows Subsystem for Linux is only available on Windows 10. If you have an older version of Windows, :ref:`install Tabbycat locally on Windows <install-windows>` instead. However, on Windows 10 computers, we recommend this method over installing directly on Windows.

Requisite technical background
==============================

It will help a lot if you have some experience with Linux, but mainly you need to be familiar with command-line interfaces, and you should be willing to install and work with the `Windows Subsystem for Linux <https://docs.microsoft.com/windows/wsl/about>`_. You might need to be prepared to familiarise yourself with aspects of WSL not covered in these instructions. While a background in the specific tools Tabbycat uses (Python, PostgreSQL, *etc.*) will make things easier, it's not necessary: we'll talk you through the rest.

A. Install Ubuntu on Windows
============================

*If you already have a Linux distribution installed on your PC, skip to* :ref:`part B <install-wsl-tabbycat>`.

Install the Windows Subsystem for Linux by `following these instructions on the Microsoft website <https://docs.microsoft.com/windows/wsl/install-win10>`_.

When you get to the part about installing a Linux distribution, we recommend the `latest version of Ubuntu <https://www.microsoft.com/store/p/ubuntu/9nblggh4msv6>`_ if you don't have an existing preference.

.. admonition:: WSL 1 or WSL 2?
  :class: note

  If you don't have any existing need for WSL 1, we recommend installing WSL 2. Microsoft's guidance indicates that WSL 2 offers faster performance for web apps like Tabbycat, and anecdotally we've found this to be the case. However, both WSL 1 and WSL 2 should work.

.. tip:: The instructions will ask you to open **Windows PowerShell as administrator**. To do this, search the Start Menu for "PowerShell", right-click Windows PowerShell, click "Run as administrator" and grant it permission to change your device. Then to run each command as instructed, paste it into PowerShell and press Enter. (As of June 2020, there are three commands.)

.. _install-wsl-tabbycat:

B. Install Tabbycat
===================

You now have a Linux subsystem running on your computer, so head over to the :ref:`instructions to install Tabbycat locally on Linux <install-linux>` and follow those (in full).
