.. _scaling:

===============================
Scaling & Performance on Heroku
===============================

If you expect your Tabbycat site to gain lots of traffic — either because it has a lot of participants or will be followed by lots of people not in attendance — there are a number of strategies to ensure that it will remain fast despite this attention. This is typically only necessary for large tournaments that will display information on the public-facing version of your Tabbycat site; and even then ongoing performance improvements should mean that only minor amounts of 'scaling' are needed.

By default a Tabbycat installation runs on Heroku's free tier. This a resource-constrained environment that has limited capacity to serve high amounts of traffic; particularly during 'bursty' events such as a draw or tab release at a big tournament. For tournaments Australs-size and up the amount of scaling needing is typically minor, however if your site does become slow you want to be able to do so quickly and with confidence — knowing what to do and how to do it ahead of time can be critical to prevent disruptions.

Improving performance will typically require paying for higher levels of Heroku services, however note that these are billed on a per-minute (not monthly) basis. If you make use of any upgrades mentioned below you will only be billed for the actual duration used — i.e. if an upgrade is listed at $100/month, but you only use it for 4 hours, the final bill will be around $0.5. As such you can make use of high-performing resources just when they are needed, without needing to pay the full monthly price of maintain the resource indefinitely.

.. note::

    Scaling for performance reasons is separate issue to that of `upgrading the database capacity <install-heroku#upgrading-your-database-size>`_ of your tab which just provides the ability to store data. That said, typically only tournaments that are large enough to need an upgraded database will be the ones that ever need to consider scaling for performance anyway.

Introduction to Scaling
=======================

Heroku's primary resource is that of a 'dyno'. Each dyno can be thought of as a running a copy of your site. Running a greater number of dynos will in general improve the ability of your site to cope with traffic because they can split up the job of loading pages amongst themselves.

Dynos can be scaled by adding more dynos ('horizontally') or by adding faster dynos ('vertically'). In general scaling horizontally should be the first and most effective strategy — typically the problem with traffic is one of *concurrency* (lots of people want information all at once). The traffic on Tabbycat sites typically fluctuates a lot, with moments of high intensity clustering around draw releases, round advances, and the final tab release. As such you generally only need to scale your dynos for very short periods of time.

In order to increase the number of dynos you first need to be using at least the **Standard 1X** level of dyno. While dynos higher than the **Standard 1X** level should help serve traffic faster having more dynos of is typically much more effective than using the higher level of dyno upgrades. Upgrading beyond **Standard 1X** is generally only required if you need additional memory (as described below) or want to use auto-scaling (also described below).

Before proceeding with this guide a crucial step is upgrading your existing '**Free**' dyno to be a '**Hobby**'-level dyno. This will enable a "Metrics" tab on your Heroku dashboard that provides statistics which are crucial to understanding how your site is performing and how to improve said performance. In general if you are at all unsure about how your site will perform it is a good idea to do this pre-emptively and keep an eye on it over the course of the tournament.

.. note::

    If pages are not loading it could be due to two things: your site being overloaded with traffic, or a bug in Tabbycat itself. Generally if you see a Heroku-branded 'application error' page that means it is the former problem, whereas a Tabbycat-branded page indicates the latter.

Scaling Dynos
=============

Once you have upgraded your dyno to the **Hobby** level the metrics tab provides a number of graphs that can be used to help identify how your site is performing. The first graph, **Events** provides an overview of any problems that are occurring:

  .. image:: images/events.png

Generally red marks, or those labelled *Critical* indicate some sort of problem, particularly if they are occurring in large numbers. Note that in the upper-right of the page you can also toggle the graphs into a 2-hour timeline for more precise measurement.

Response Time & Throughput
--------------------------

  .. image:: images/response-time.png

The response time is the amount of time it takes a dyno to load a page and serve it to your users. Smaller response times are thus good, and long response times (over ten seconds) indicate a site that is straining to serve its content.

Heroku dynos have a maximum response time of 30 seconds, at which point they will stop serving the request — something users see as an error or as a page that never loads. Thus if you see the graph is near 30 seconds at any point you need to try and diagnose what is causing this and add more resources to reduce the response time.

.. note::

    You can toggle the percentiles in this graph here. Any problems problem are much more severe if it affects the 50th percentile rather than the 99th and represents a site that is probably not loading for the majority of its users rather than not loading 1 time out of 100.

Closely related to this is the **Throughput** graph (further down) which shows how many pages your site is serving a second. Normally this is not particularly interesting, however note that the red part of the bar graph shows the amount of failed page requests. Like the **Response Time** graph this shows serious issues with the site — normally this red portion should be well below 1rps (and ideally 0rps). If it is above 0.5 it represents a site that is producing a significant number of failed page loads.

You can verify if pages are not being served to users by checking the **Events** graph and looking for H12 errors. If these are occurring you probably want to add more dynos. A large amount of H13 errors can also be a cause for concern.

Dyno Load
---------

    .. image:: images/dyno-load.png

This graph shows how well your dynos are being utilised. It is scaled relative to the total number of dynos you are running (or have run previously). So if you have 10 dynos and the bar graph is near the '10' this shows that each dyno is being utilised 100% (either on average over a 1-minute period or as the maximum use over a 1-minute period).

Generally if this bar graph is hitting the top it will represent a site that is slow or failing to load pages — if each dyno is busy it can't serve a new page until it is finished. This issue can often compound, with more traffic coming in than it is possible to serve and clear.

If your average, rather than maximum, dyno load is approaching the upper limit of however many dynos you are running now (remember the y-axis will often exceed however many dynos you are currently running) that is a very good sign that you should increase the quantity of dynos being run. Continue adding dynos and evaluate how this effects load so that the bar is not hitting its limit.

If you are consistently needing to scale things (or having previously had issues and are expecting a very heavy burst of traffic) it may be worth upgrading to the **Performance-M** dyno type, which will then allow you to enable the *Auto-scaling* feature. This will automatically add dynos as needed to cope with traffic, and remove them when they become unnecessary. This is very effective, however note that this dyno-type is $250/month per dyno and will self-add dynos (within an upper limit you can specify). While this is not a huge price on a per hour/minute basis (even running 30 for an hour is only $10) you definitely want to ensure you keep a close eye on it and turn it off when it is not necessary.

Memory Usage
------------

    .. image:: images/memory-use.png

It is very rare that Tabbycat sites will hit the memory limits of the Free or Hobby level dynos — its almost always hovering around 256mb of the (standard dyno) limit of 512mb. However if the graph is approaching the dashed line you may want to first restart the dynos (in the *More* dropdown in the upper-right) and see if that resolves it.

You can also confirm that memory limits are causing the app to fail by checking for the presence of R14 errors in the Events chart. If your site continues to come very close to that memory limit you will want to upgrade your dynos to the higher level dynos which have increased memory.

Understanding Caching
=====================

When a page is 'cached' it means that the site has stored a copy of the final output of the page. This means that it can then send that data to a user without needing to fetch the data from the database, run any calculations, and format the results. Pages that are cached will serve quickly — if a page is taking more than a few seconds to load it usually means that page has not been cached (or your site is having too much traffic to serve pages quickly in general). The downside of this is that changes to the underlying data wont update until the cache has 'expired' and is regenerated. So for example a cached copy of the draw will not reflect a change to its adjudicators or a newly-enable public tab page will not show up in the menu.

By default Tabbycat caches public pages according to two levels: a 1-minute timeout and a 2-hour timeout. The only pages on the 2-hour timeout are those that come with a full tab release — such as speaker standings, the motions tab, etc. All other public pages, such as the draw and homepage are on the 1-minute timeout to ensure data is up to date.

Often performance problems come when a popular page, such as a newly-release draw or standings page gains a large amount of traffic (such as by people constantly refreshing the draw). If the page hasn't finished caching it has to do a full page calculation for each of those new loads, which will spike the amount of resource use.

One way to help mitigate this — particularly during the main tab release — is to try and load those pages first yourself to ensuring the cache is populated before other people access it. To do so you would generally open a new private browsing tab, and navigate to the specific page(s) immediately after you have enabled them. This may require going to the URL directly rather than relying on the homepage or menu (which may not have been updated to show the new information).

If you want you can also increase the 1-minute timeout for the pages that are popular during the in-rounds, by going to the **Settings** section of your Heroku dashboard, clicking *Reveal Config Vars*, and creating a new key/value of ``PUBLIC_PAGE_CACHE_TIMEOUT`` and `180` (to say set the timeout to be 3 minutes / 180 seconds). This should only be necessary as a last resort however. Turning of public pages is also an option.

If you ever need to clear the cache (say to force the site to quickly show an update to the speaker tab) you can install `Heroku's Command Line Interface <https://devcenter.heroku.com/articles/heroku-cli>`_ and run the following command, replacing ``YOUR_APP`` with your site's name in the Heroku dashboard::

    $ echo " FLUSHALL\r\n QUIT" | heroku redis:cli -a YOUR_APP --confirm YOUR_APP

Redis Limits
============

Redis is a serve that handles storing and serving your app's cache on Heroku. On the free tier it has a limit of 20 'clients' — i.e. 20 simultaneous users. Generally users are connected to redis for very short periods of time, so even an Australs-sized tournament under heavy load will not exceed that limit. However exceeding the limit may cause errors or slow the site.

    .. image:: images/clients.png

However, you can monitor this in your Heroku Dashboard by going to the **Resources** tab and clicking on the purple Redis link. The **Clients** graph here will show you how close you are to the limit. If you need to increase the limit or want to take precautions, you can go back to the **Resources** tab and click the **Edit plan** link. The **Premium 0** plan will increase the limit to 40 and will self-install seamlessly.

Postgres Limits
===============

In a similar manner to Redis the free tier of the postgres database services has a limit of 20 'connections'. As with Redis, it is rare that a Tabbycat site will exceed this limit; most Australs-sized tournaments will see a maximum of 15 connections of their time.

    .. image:: images/connections.png

You can monitor this in your Heroku Dashboard by going to the **Resources** tab and clicking on the purple Postgres link. The **Connections** graph here will show you how close you are to the limit. Note that the first tier up from the 'free' Hobby tier has a connection limit of 120 and is probably what you should be `running at large tournaments anyway <install-heroku#upgrading-your-database-size>`_.

Mirror Admin Sites
==================

If you *really* want to be safe, or are unable to resolve traffic issues and unable to quickly complete tasks on the admin site, it is possible to create a 'mirror' of the tab site just for admin use. This site can be configured to share the same database as the primary site — meaning it is in effect always identical — but because it is at a separate URL it wont have to respond to public traffic which is much higher than that of admin users.

.. warning:: This requires some technical knowledge to setup and hasn't been rigorously tested. In our experience it works fine but we haven't tested it extensively. If using this make sure you backup (and now how to restore backups) before setting one up.

To do so you would deploy a new copy of Tabbycat on Heroku as you normally would. Once the site has been setup, go to it in the Heroku Dashboard, click through to the **Resources** tab and remove the Postgres and Redis Add-ons. Using the `Heroku Command Line Interface <https://devcenter.heroku.com/articles/heroku-cli>`_ run this command, substituting ``YOUR_APP`` with your *primary* tab site's name (i.e. the app that you had initially setup before this)::

    $ heroku config --app YOUR_APP

Here, make a copy of the ``DATABASE_URL`` and ``REDIS_URL`` values. They should look like ``postgres://`` or ``redis://`` followed by a long set of numbers and characters. Once you have those, go to the *Settings* tab of the Heroku dashboard for your *mirror* tab site. Click **Reveal Config Vars**. There should be no set ``DATABASE_URL`` or ``REDIS_URL`` values here — if there are check you are on the right app and that the add-ons were removed as instructed earlier. If they are not set, then add in those values, with ``DATABASE_URL`` on the left, and that postgres url from earlier on the right. Do the same for ``REDIS_URL`` and the redis url. Then restart the app using the link under **More** in the top right.

Once you visit the mirror site it should be setup just like the original one, with changes made to one site also affecting the other (as if they were just a single site).

