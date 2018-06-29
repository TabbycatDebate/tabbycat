.. _scaling:

=================
Scaling on Heroku
=================

If you expect your tournament to gain lots of traffic — either because it has a lot of participants or will be followed by lots of people not in attendance — there are a number of strategies to ensure that your Tabbycat site will perform despite this attention.

By default a Tabbycat installation runs on Heroku's free tier. This a resource-constrained environment that has limited capacity to serve high amounts of traffic; particularly during 'bursty' events such as a draw or tab release.

Improving performance will typically require paying for higher levels of Heroku services, however note that these are billed on a per-minute (not monthly) basis. If you make use of any upgrades mentioned below you will only be billed for the actual duration used — i.e. if an upgrade is listed at $100/month, but you only use it for 4 hours, the final bill will be around $0.5. As such you can make use of high-performing resources just when they are needed, or even over the (relatively) brief period of time a tournament runs, without needing to pay the full monthly price of maintain the resource indefinitely.

Note this is a seperate issue to that of database capacity.

Introduction to Scaling
=======================

Heroku's primary resource is that of a 'Dyno'. Each dyno can be thought of as a 'copy' of your app. Running a greater number of copies will in general improve the ability of your site to cope with traffic.

Dynos can be scaling by adding more dynos 'horizontally' or by adding faster dynos 'vertically'. In general horizontally should be the first and most effective port of call — typically the problem with traffic is one of *concurrency* (lots of people want information all at once). Faster dynos will help with this too, but not as much as having more dynos. Upgrading this dyno types is generally only required if you need additional memory (as described below) or as a last resort.

Before proceeding with this guide, especially if you are uncertain about how much traffic your tournament will get, a crucial step is upgrading your existing 'Free' dyno to be a 'Hobby'. This will enable a "Metrics" tab on your Heroku dashboard that provides statistics which are crucial to understanding how your site is performing and how to improve said performance.

Errors vs Resources
===================

Page can not be loading due to errors; i.e. bugs. That usually isn't the case however, particularly if its generally slow rather than just a particular page that wont load. Confusingly however moments of very high load can show "Application Errors" (usually heroku-branded rather than tabbycat-branded) which are not bugs but just critical resources being unavailable.

Scaling Dynos
=============

HOW TO: restart an app

Once you have upgraded your Dyno to a 'Hobby' dyno the metrics tab provides a number of graphs. These can be interpreted as follows:

- Response Time tab
    - The response time is the amount of time it takes a dyno to load a page and serve it to your users. Smaller response times are thus good, and long response times (over ten seconds) indicate a site that is straining to serve its content.
    - Heroku dynos have a maximum response time of 30 seconds, at which point they will stop serving the request — something users see as an error or a page that never loads. Thus if you see the graph is near 30 seconds at any point you need to try and diagnose what is causing this and add more resources to ameliorate this.
    - Note that you can toggle the percentiles here. The problem is much more severe if it affects the 50th percentile rather than the 99th and represents a site that is probably not loading for the majority of its users.
    - Closely related to this is the Throughput tab which shows how many pages your site is serving a second. Normally this is not particularly interesting, however note that the red part of the bar graph shows the amount of failed page requests. Like the Response Time graph this shows serious issues with the site — normally this red portion should be well below 1rps (and ideally 0rps). If it is above 0.5 it represents a site that is producing a significant number of errors.
    - You can verify if pages are not being served to users by checking the Events chart and looking for H12 errors. If these are occuring you probably want to add more dynos as described below. A large amount of H13 errors can also be a cause for concern.
- Memory Usage tab
    - It is very rare that Tabbycat sites will hit the memory limits of the Free or Hobby level dynos. If the graph is approaching the dashed line you may want to restart the dynos and see if that resolves it.
    - *You can confirm that memory limits are causing the app to fail by checking for the presence of R14 errors in the Events chart*
    - *If it continues to come very close to that memory limit you will want to upgrade your dynos to the Standard-level dynos which have increased memory.*
- Dyno Load tab
    - This graph shows how well your dynos are being utilised. It is scaled relative to the total number of dynos you are running (or have run previously). So if you have 10 dynos and the bar graph is near the '10' this shows that each dyno is being utilised 100% (either 100% on average over a 1-minute period or 100% max over a 1-minute period)
    - Generally if this bar graph is hitting the top it will represent a site that is slow or failing to load pages — if each dyno is busy it can't serve a new page until it is finished, and this can compound.
    - You should note how many dynos you are currently running and check how close the graph is coming to that number. I.E. if you are currently running 1 Dyno and the load is near 100% of "1" that is a very good sign that you should add more dynos. Continue adding dynos and evaluate how this effects load so that the bar is not hitting that limit.
    - If you are consistently needing to scale things (or expecting a heavy burst of traffic) it may be worth upgrading to the Performance-M dyno type, which will then allow you to enable the Autoscaling feature. This will automatically add dynos as needed to cope with traffic, and remove them when they become unnecessary. This is very effective, however note that this Dyno-type is $250/month per dyno and will self-add dynos (within an upper limit you can specify). While this is not a huge price on a per hour/minute basis (even running 30 for an hour is only $10; and it is unlikely to make that many) you definitely want to ensure you keep a close eye on it and turn it off when it is not necessary.

Understanding Caching
=====================

Another way to improve performance is to increase the duration of caching; although this has the drawback of having information on the public-facing site of your page be out of date for longer.

To step back: when a page is 'cached' it means that the site has stored a copy of the final output of the page. This means that it can then send that data to a user without needing to fetch the data from the database, run any calculations, and format the results. Pages that are cached will serve quickly — if a page is taking more than a few seconds to load it usually means that page has not been cached (or your site is having too much traffic to serve pages quickly in general). The downside of this is that changes to the underlying data wont update until the cache has 'expired' and is regenerating. So for example a cached copy of the draw will not reflect a change to its adjudicators or a newly-enable public tab page will not show up in the menu.

Only public-facing pages are cached. By default the caches of most public pages expire every 60 seconds, while 'tab release' pages, such as the speaker tab, will expire every two hours.

- PUBLIC_PAGE_CACHE_TIMEOUT heroku variables
- the bursting problem
- clearing the cache

Redis Limits
============

Postgres Limits
===============

Worst Case
==========

- i.e. if you have crucial admin activities to do but the public site is overwhelming and the scaling approaches above are not working
- turn off public pages
- maybe restart the site; try and get in first
- note this particularly affects adjudicator allocations as they take a long time

Duplicate Sites
===============

- check if this works