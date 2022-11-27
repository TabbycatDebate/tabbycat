.. _install-render:

====================
Installing on Render
====================

.. admonition:: IMPORTANT
  :class: error

  Setting up Heroku on Render is currrently in beta and is somewhat unreliable. Use Heroku for a more reliable option.

Render is a web hosting platform, similar to Heroku. Like Heroku, it provides a similar '1 click' method of deployment that should be approachable to people without experience in deploying web applications. Support for deploying Tabbycat to Render is currently **in beta**.

.. admonition:: Warning
  :class: warning

  The most important difference between Render and Heroku is that **after 90 days, Render's free-tier database will stop working and delete all your data**. If you want to keep your tab data around for the long term, you must backup your data and host it elsewhere after the tournament ends

Please also note:

- Although Tabbycat is setup to run within the free-tier of Render, you may need to add a credit card to your account in order to create your account
- While Render might run faster for small tournaments, we are unclear how well it runs at a larger scale and how best to employ Render's scaling tools

To deploy to Render, follow the instructions below.

1. Signup
=========

`Follow this link <https://dashboard.render.com/register?next=/>`_ and sign-up for the Render service. Login when finished, and navigate to your *Dashboard*.

2. Setup
========

.. image:: https://render.com/images/deploy-to-render-button.svg
  :target: https://render.com/deploy?repo=https://github.com/TabbycatDebate/tabbycat/

Click the button above. Enter whatever you want as the **Service Group Name** and leave "Branch" as it is.

Then, enter your email and Time Zone in the fields. Time zones are formatted as per Heroku — copy of a "TZ database name" `from this list <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List>`_, e.g. *Europe/Copenhagen*.

Then, click "Apply" at the bottom of the page. The button will disappear.

Wait it  a few minutes then go to your *Dashboard*. It may take up to 30 minutes for all items have a *STATUS* of "Deploy succeeded" or "Available" and you may need to refresh the page to see these updated status.

3. Login
========

When everything is successful/available, click through to the "Web Service" item on your Render Dashboard to see the URL of your site below the title. Open the URL to complete the normal Tabbycat admin account setup.

Note that this URL cannot be changed unless you `add a custom domain using a URL you already own <https://render.com/docs/custom-domains>`_.
