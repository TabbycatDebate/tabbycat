.. _install-calico:

====================
Installing on Calico
====================

When running Tabbycat on the internet, you can choose to use `Calico <https://calicotab.com/>`_ for hosting. Calico was designed to host Tabbycat sites without needing extra configuration. Naturally, this requires you to have a Calico account.

Click `this link <https://calicotab.com/tournaments/new/>`_!

This is the easiest way to deploy an instance of Tabbycat online. It requires no technical background.

If you don't already have a Calico account, it'll prompt you to create one. Once you're logged in, choose a name for your installation, then scroll down and click **Create Site**. After you've paid the 50CAD fee, it will redirect you to your new site, and you can log in with your Calico account. Once finished, open the site and from there you can easily set up a demo data set (if you just want to learn Tabbycat) or use the data importer to set up a real tournament.

.. note:: Your Calico account and the accounts on your site are independent, i.e. changing passwords on a site does not change your Calico password.

Calico does not allow for the use of the ``importtournament`` command, but custom CNAME records pointing to a site do work for custom domains.
