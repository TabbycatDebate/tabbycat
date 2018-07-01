.. _upgrading:

==================
Upgrading Tabbycat
==================

Generally only want to upgrade copies of tab sites that are used on an ongoing basis for multiple tournaments, or if there is a bugfix release between when you setup your site and when the tournament is running.

.. note::

  Going from any version of Tabbycat 1 to any version of Tabbycat 2 won't work with the below instructions — check out the CHANGELOG for the 2.0 version for details of how to perform this upgrade.

Upgrading a Local Copy
======================

Assuming you haven't made any changes to the Tabbycat code, upgrading a locally installed copy should just be a matter of `downloading the latest source code <https://github.com/TabbycatDebate/tabbycat/releases/latest>`_ and replacing the existing files with the new ones. If you used git to download these files initially you can just pull down the latest copy of the master branch to do this.

You would then repeat the "Install Tabbycat" instructions for your original installation method.

Upgrading on Heroku
===================

The easiest way to upgrade a Heroku site is to create an account on Github and then to `'fork' <https://help.github.com/articles/fork-a-repo/>`_ the `Tabbycat repository <https://github.com/TabbycatDebate/tabbycat>`_.

Once you have done this you can login to your Heroku Dashboard, go to your app, and then navigate to the Deploy tab. In this tab, adjacent to *Deployment method* select the GitHub option. This will bring up a new 'Connect to GitHub' section where you can search for 'Tabbycat' to find the copy of the repository you made earlier and connect it.

  .. image:: images/deploying.png

Once connected a new *Manual deploy* section will appear. Make sure you select the *master* branch (not develop) and then click *Deploy Branch*. This will then show the app deploying and notify you when it has finished; which may take several minutes.
