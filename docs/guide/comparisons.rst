.. _comparisons:

========================
Tab Software Comparisons
========================

If you're reading this, you're probably interested in using Tabbycat, and wondering how it compares to other options. Perhaps you're a long-time user of another tab system, and wondering what Tabbycat can do better. This page is our effort to help answer this. Tabbycat's been around since 2010, but since BP support is a recent addition (2017), we thought it would be useful to outline the differences between Tabbycat and other BP software.

Obviously, this page is written by the developers of Tabbycat, and naturally, we have our biases. But rarely is there a single best option for everyone and every situation: different tab programs imagine the tabbing process in a different ways and have made unique trade-offs in their development process and design decisions. So we've tried to be as fair and accurate as we can, and we've consulted experienced tab directors (other than us!) and chief adjudicators to help provide a balanced overview.

At present, this guide just focuses on the major options available for the British Parliamentary format, although we'd like to expand this to incorporate the other formats that Tabbycat supports at some point in the future. As with all of our documentation, the source for this page `is on GitHub <https://github.com/TabbycatDebate/tabbycat/blob/develop/docs/guide/comparisons.rst>`_, and we welcome feedback and contributions.

On feature lists
----------------

In the first draft of this document, we had a table that listed every feature we could think of, along with which software does and doesn't support it. This ended up not being a great idea, for a couple of reasons.

Firstly, the largest feature disparities are for relatively niche features. All of the software discussed can do the basics necessary to run a tournament: generate draws, allocate adjudicators, enter results, etc. As a result, we will — like a good whip speech — be comparative and note key feature disparities when discussing each alternative software directly.

Secondly, we felt that the 'checklist' approach to comparing tab software would do a disservice to the reasons you would actually choose one software over another. Except where a niche capability is essential, raw technical specifications rarely define the experience of using a product such as a phone, a car, or indeed, tabbing software. With Tabbycat, we've spent eight years continuously refining the tabbing workflow and smoothing out rough edges, and we believe you'll find the result extremely user-friendly and robust. As always, the best way to check this out is by :ref:`setting up a demo site and taking it for a spin <install-heroku>`!

Comparison with Tabbie2
-----------------------

Centralised site vs individual sites
====================================

Tabbie2 and Tabbycat are both internet-based systems. Tabbie2 hosts all tournaments on a single site. However, when using Tabbycat, each tournament or organisation sets up its own site. Each model has its advantages and disadvantages in different areas:

**User identification**. Tabbie2's centralised model allows for site-wide user accounts for all tournament participants. This means that they can use the same login information for all tournaments, and perform tasks such as submitting ballots and feedback through that unified account. If you're in an established circuit, most of your participants probably already have user accounts which are identified and collected (via e-mail addresses) during registration. If you're in a newer circuit, or one where Tabbie2 is rarely used, most of your participants will probably need to create an account — a process which Tabbie2 handles by e-mailing them a request to do so when that person is added to your tournament.

In Tabbycat's decentralised model, there is no persistent 'account' for tournament participants on each tab site or across different tab sites. Indeed, the only people who can log in to the site are those who have been given accounts by the tab director, such as tab staff and members of the adjudication core.

For secure e-ballot and e-feedback submissions, Tabbycat assigns a "private URL" to each participant. This is essentially a password that allows a participant to only submit data that they should have access to in that specific tournament. This means participants don't need user accounts and you don't need to collect user account information; however if your tournament uses e-ballots or e-feedback you will need to distribute those private URLs to participants. Tabbycat can e-mail these to participants for you, or print them to give them to participants, or you could distribute the URLs using your own means.

**Control over data**. Some participant information in Tabbie2 is shared between tournaments, like their names and conflicts (discussed below). This means participants can manage it directly through their user accounts, without needing to go through you. On the other hand, this requires your participants to co-operate in keeping their accounts up to date, and to provide the correct e-mail address during registration (you'd be surprised how many don't). Furthermore, participants may look to you for assistance, and your ability to help is limited to directing them through Tabbie2 channels—easy enough if they forget their password, but not so much if they forget their account's e-mail address.

Because each Tabbycat site is its own, you'll need to collect and import all participant details yourself. This might seem like more to do, but it also means there's no need to match your data to existing accounts, which can be time-consuming and prone to participant error. It also means you can freely change data, for example, to correct a participant's name or institution, or to add data like conflicts on an ad-hoc basis.

**Data privacy**. Conflicts are typically entered into the tab, and are sensitive information. Tabbie2's centralisation allows for conflicts to be self-nominated by users and stored in their user accounts. This, in theory, saves the need for users to report conflicts to tab directors and other tournament staff. In practice, however, only special "super" users on Tabbie2 have access to the stored conflicts of users (otherwise anyone could access a user's conflicts by creating a new tournament and adding that user as a participant), so many tournaments need to collect this information from participants anyway.

Tabbycat's decentralised model means that no-one will have access to conflict information except for the tab staff of each individual instance of Tabbycat. Unlike Tabbie2, Tabbycat's developers do not have any access to your tournament's data — conflicts or otherwise. However, to help us continually improve the software, Tabbycat does send error reports to its developers if there is a serious bug or crash in the code, which could potentially contain confidential information depending on which page triggered the report. As a result of Tabbycat's decentralised data storage, each tournament does need to collect and enter conflicts as part of their registration process.

**When things go wrong**. In our view, this is probably the most important factor. Obviously, we all hope you never have to fix things. But no software is perfect, and software developed by volunteers in their spare time (as both Tabbie2 and Tabbycat are) is especially imperfect. On occasion, glitches or edge cases occur, and fixing them requires you to directly edit the offending data in the database. Being able to do this without assistance can be the difference between a delay of minutes and a delay of hours.

In Tabbycat, because it's your site, you have full control of the database, and can edit it through Tabbycat's "Edit Database" area. This allows you to fix things (or break things, if you're not careful!). Tabbie2's centralisation prevents this—for obvious reasons, only Tabbie2's developers have direct database access, which makes their intervention necessary if direct database access is required to resolve a problem.

Running your tournament
=======================

Tabbie2 and Tabbycat have broadly similar workflows for running rounds; at least on paper. Key differences are discussed below:

**Data import**. Tabbie2 takes CSV files for import. Tabbycat has a CSV file importer, but it's (for now) only accessible through a command-line interface and is only expected to be used for large tournaments by experienced tab directors. As a more user-friendly alternative, Tabbycat also has an import wizard that's designed to make it easy to copy and paste CSV data. This works well for small and medium scale tournaments, but is cumbersome for large ones.

**Public interface**. Tabbycat can optionally publish the entire draw, as well as current team point standings and results of previous rounds, online. Tabbie2 shows to a logged-in user information about the debate that user is in for that round, but doesn't allow people to check up on people who are not themselves.

**Position rotation**. Tabbie2 uses an algorithm known as the "Silver Line algorithm", which keeps swapping pairs of teams until no further improvement is found. Because it stops at any 'local optimum', this method isn't guaranteed to be the best possible distribution of positions, and for large tournaments it often isn't. Tabbycat instead uses the `Hungarian algorithm <https://en.wikipedia.org/wiki/Hungarian_algorithm>`_, an well-known algorithm that finds the (globally) optimal allocation of positions. (One might describe this algorithm, in technical terms, as 'powerful'.) Tabbycat also produces a position balance report, so that in every round you can see which teams have unbalanced position histories.

**Venue allocations**. Both Tabbie2 and Tabbycat allow for debate venues to be automatically assigned and manually edited. Tabbycat also allows you to specify 'venue constraints' that can automatically match particular participants with their accessibility requirements, or alternatively allow for tournament staff, such as a convenor or chief adjudicator, to be allocated rooms close to the briefing hall or tab room.

**Ballot entry**. Both Tabbie2 and Tabbycat support entering ballots online ('e-ballots') and entering ballots from paper from the tab room. Tabbie2 was built with e-ballots in mind, while Tabbycat was originally built for tab room staff, and the ballot entry paradigms reflect that. Both are flexible, just a little different—the best way to understand the difference is to try a demo of each. Also, Tabbycat takes note of the order in which speakers in a team spoke (i.e. who was PM and who was DPM), whereas Tabbie2 just records scores.

As discussed earlier in *User identification*; Tabbie2's e-ballots are tied to unified user accounts, whereas Tabbycat's e-ballots are tied to per-tournament and per-adjudicator 'private URLs'.

**Break and speaker categories**. Tabbie2 has ESL, EFL and novice markers, which you can enable in a tournament's settings. Tabbycat supports user-defined break and speaker categories, so if your tournament has ESL, EFL, novice or any other form of category, you can define and customise those categories as needed.

**Adjudicator allocation algorithm**. Both Tabbie2 and Tabbycat use an algorithm to recommend an initial allocation of adjudicators to debates. In principle, they both work by assigning "costs" to allocations, and trying to find the minimum-cost assignment. Some notable differences:

    - Tabbie2 uses simulated annealing, which is not guaranteed to be optimal and technically needs to be tuned to be effective (which you're probably not doing). Tabbycat uses the Hungarian algorithm, which guarantees an optimal solution.
    - On the other hand, the Hungarian algorithm can't account for relationships between adjudicators on a panel, so adjudicator-adjudicator conflicts aren't considered by Tabbycat's algorithm (though they are highlighted in the interface).
    - Tabbycat's cost function is simpler and more naive. On the other hand, Tabbie2's is more complicated and can be rather opaque (even if you read its source code).
    - Tabbie2 allows for single-gender panels to be charged an additional cost. Tabbycat's algorithm doesn't, but the interface does provide a way to easily check for this visually.
    - Tabbie2 automatically calculates the importance of a room based on its bracket (team points). In Tabbycat, debate importance can be assigned for all debates automatically based on on a room's bracket or the quantity of live break categories inside it. Instead of — or subsequent to — automatic classification any importance  value can be manually tweaked as desired. These options mean there is a greater flexibility in determining which debates the allocation algorithm should prioritise.

**Adjudicator allocation interface**. While both interfaces use drag and drop interactions, and allow for color highlights to help identify adjudicators by gender, region, and feedback rating, Tabbycat's allocation interface was designed to be usable on both small screens and projectors, and has a number of extra features that can help inform allocations. These features include:

    - Clashes are shown directly in the interface when they apply, but dragging an adjudicator will also show you the potential conflicts that would occur if they were relocated in a new panel. This can make it much easier to avoid creating new clashes when shifting adjudicators around the draw.
    - An inline display of an estimate of whether a team is 'live' for each of their break categories — i.e. whether they are 'safe' (have enough points to break); 'dead' (cannot gain enough points to break); or 'live' (still in contention).
    - 'History' conflicts (where an adjudicator has seen a team before, or previously was on a panel with another judge) are displayed so they can be avoided.
    - Each adjudicator is present as occupying a particular position (chair, panellist, trainee) rather than having those positions calculated automatically.
    - Chairs can be 'swapped' by dragging adjudicators on top of each other, and an 'unallocated' area can be used to view and store adjudicators that have not been allocated.

**Adjudicator feedback customisation**. Both Tabbie2 and Tabbycat have built-in adjudicator feedback forms, and allow you to specify the questions on the feedback form. Notable differences:

- Setting up questions is painless on neither system. Tabbycat requires you to use the Edit Database area; Tabbie2 makes you click through a slightly more opaque maze of pages and forms.
- Tabbycat allows for a richer range of types of questions than Tabbie2 does.
- Tabbie2 allows you to specify different questionnaires for team-on-chair, chair-on-panellist and panellist-on-chair. Tabbycat only differentiates between team-on-adjudicator and adjudicator-on-adjudicator.
- Tabbycat gives you more control over who is expected to submit feedback on whom; e.g. whether teams submit on panellists, and whether panellists submit on each other. In Tabbie2, you can effect this with blank questionnaires, but only for the three options listed above.
- Tabbycat can, optionally, automatically incorporate feedback into adjudicator scores using a naive weighted average with the adjudicator base score. This can be disabled by simply setting feedback weight to zero, as some adjudication cores prefer. Tabbie2 has no ability to automatically incorporate feedback.
- Tabbycat produces a "shame list" of unsubmitted feedback, which you can optionally publish on the public-facing site to try to incentivise submission.

(How participants access adjudicator feedback submission is discussed in *User identification* above.)

Other considerations
====================

**Offline availability**. If you like, you can also install Tabbycat on your own computer, rather than host it as website on a server. This means that you can use it offline. However installing Tabbycat in this manner will require the (at least brief) use of a command line interface.

**Cost**. Tabbie2 is free to use. Tabbycat is free to use for not-for-profit, not-for-fundraising tournaments; tournaments for profit or fundraising must make a donation of A$1 per team. In addition, larger tournaments that run on Tabbycat's recommended web host (Heroku) may need to purchase an upgraded database service (the free tier has storage limits) which will cost around ~US$3 to use for the duration of a week-long tournament.

**Documentation**. Tabbycat has `relatively extensive documentation <http://tabbycat.readthedocs.io/en/stable/>`_ that can be useful for learning how to use a particular feature or understanding what is happening at a technical level.

**Hosting location**. Tabbycat recommends using Heroku, an established cloud platform service for deploying web applications. Heroku is in turn hosted on Amazon Web Services (AWS). Both Heroku and AWS are highly reliable and widely used; downtime for both has historically been (at worst) less than 0.05% over an annual period. Tabbie2 is hosted on `Uberspace <https://uberspace.de/>`_; a pay-what-you-want web hosting service. To the best of our knowledge, uptime statistics are not available.

**Multi-format support**. If you are interested in tabbing both four- and two- team formats there may be some value in using and learning Tabbycat as it will let you use the same software in both settings.

Comparison with Tournaman
-------------------------

Native app vs web app
=====================

The crucial strength — and limitation — of Tournaman is that it is a Windows desktop application. Naturally, being a desktop app limits the features it can offer, relative to web apps like Tabbycat or Tabbie2, since it can't offer any online access. On the other hand, working with a desktop app can often be simpler than a web app.

**Installation**. You'll need to run (or emulate) a Windows machine to run Tournaman. Assuming you're using Windows, Tournaman's installation process is easy and familiar.

Tabbycat has a simple one-click installation process if you're deploying online (:ref:`to Heroku <install-heroku>`). However, if you want to run Tabbycat on your own computer rather than a website, this is substantially more complicated. Local installations of Tabbycat work by having your computer emulate a web server, and while we've tried to make this as accessible as possible, a technical background is definitely helpful for this. Using our :ref:`Docker-based method <install-docker>` should be simple, but it's not 100% reliable, and if it fails it can be difficult to figure out why. If internet access is available, we recommend running Tabbycat on Heroku.

**Online features**. Because Tournaman runs fully offline, it naturally can't support many internet-based features: electronic ballots, online publication of draws and live team standings, and integrated tab release. Typically, if you wanted to publish anything online from Tournaman, you'd do so by publishing the files that Tournaman generates locally. In Tabbycat, all of these are built in, so there's a single website for all tab information.

**Multi-user access**. Tournaman can be configured to allow networked ballot entry, but in order to set it up, you need to be comfortable with basic computer networking. This works best on small isolated networks that you control directly, e.g. a dedicated router set up in the tab room. It's not a great idea to set this up on computers connected to a university-wide network: many IT departments won't permit it, and even if they do, it's insecure, since anyone on the network can access it.

Tournaman's multi-user access is designed primarily to allow tab assistants to enter data. Key administrative tasks, such as draw generation and adjudicator allocation, must still be done on the computer on which Tournaman is installed. In contrast, web-based systems like Tabbycat and Tabbie2 allow users to login from any internet-connected device to access the functionality permitted by their account. This is often extremely useful if, say, you want to log in to a lectern computer, or have tab assistants work on mobile devices that they have with them.

If you choose to install Tabbycat offline (rather than on Heroku), it's also possible to have the computer on which the local installation resides serve the website to other computers on the same network. This then permits anyone on the same network to access the "local" installation as if it were hosted on the internet. However, like Tournaman, such a configuration requires at least basic networking experience, and for security reasons is only advisable on small isolated networks that you control.

**Backups and portability**. Both Tournaman and Tabbycat (unlike Tabbie2) store data in a way that is completely accessible to you. Tournaman does this by saving files on your computer's hard drive, while Tabbycat stores data in a SQL database that belongs to you.

It should be emphasized that in both Tournaman and Tabbycat, actually needing to revert to a backup is extremely rare. Almost always, any glitch or error that breaks the tab can be resolved by editing data directly, without needing to "roll back" to a previous state. In Tournaman, this is done by editing the files that it writes to your hard drive (they're just XML files). In Tabbycat, this is done through the "Edit Database" area.

Tournaman's storage of data as XML files makes backups easy, although effort should be made to have backups stored on other computers or the cloud  (e.g. on Dropbox) in case the tab computer breaks or is lost. Restoring data from those backups (or transferring the tab to a different computer) is typically a simple process of copying the files back to the original location.

As for Tabbycat, in online installations, backups can be taken easily using Heroku's `database backup capability <http://tabbycat.readthedocs.io/en/stable/features/backups.html>`_. However, restoring backups requires you to have the Heroku command line interface installed. In offline installations, PostgreSQL's "dump" and "restore" commands are recommended, and may require some perseverance to get going reliability, particularly if you don't have prior SQL experience.

Generally there is no need for data portability when working with an online copy of Tabbycat — the website can be accessed anywhere. However if working with an offline/local copy, a tab can be transferred between machines by creating a backup of the database and restoring it to the other machine's database (doing so requires technical knowledge).

Running your tournament
=======================

**Adjudicator feedback**. Tournaman lets you assign judges rankings, however it does not directly manage or assist the process of collecting judge feedback. As such tab directors generally need to run a parallel feedback system, and then manually copy over changes to an adjudicator's ranking into Tournaman itself. In contrast, Tabbycat has integrated methods for collecting judge feedback that allow it to be more easily issued, collected, viewed, and automatically translated into modifications to an adjudicator's rank.

**Adjudicator allocation**. Tournaman has a fixed judge ranking scale and (from what we understand) has a relatively fixed procedure for allocating panels according to their absolute ranks. We are unsure about the exact mechanics of how this works, but broad details are `available here <https://www.facebook.com/notes/harry-mcevansoneya/tournaman-judge-ranking-scale-advice-for-future-cas/10151964404693002/>`_.

As with the discussion of allocation interfaces vis-à-vis Tabbie2, there are a number of features in the Tabbycat allocation interface that mean it is more easily used in a collaborative setting and can display additional information to inform draws.

**Flexibility in draw rules**. As we've said, all major tab systems are WUDC-compliant. But if you want to deviate from WUDC rules, Tournaman has a few more options. Whereas Tabbycat allows you to use intermediate brackets (rather than pull-ups), Tournaman allows you to sacrifice power-pairing integrity for position balance (though this generally isn't necessary to achieve position balance), fold within brackets and avoid teams hitting their own institution. On the other hand, Tabbycat allows you to tune how position balance trades off between teams (which the WUDC constitution doesn't precisely specify).

Other considerations
====================

**Stability and development**. Tournaman has been in use for over a decade and is generally considered to be stable and reliable. However, new features are relatively rarely added, and its being a native app means that it doesn't boast as many features as Tabbycat or Tabbie2.

**Cost**. Tournaman is free to use. Tabbycat is free to use for not-for-profit, not-for-fundraising tournaments; tournaments for profit or fundraising must make a donation of A$1 per team. In addition, larger tournaments that run on Tabbycat's recommended web host (Heroku) may need to purchase an upgraded database service (the free tier has storage limits) which will cost around ~US$3 to use for the duration of a week-long tournament.

**Availability of source code**. Tournaman's code is closed-source, meaning it is not publicly available. If you do not have any coding experience this is probably not relevant to you, but if you do, having access to the source of Tabbycat can help you understand how the program works and customise it as needed.

Comparison with hand tabbing
----------------------------

Hand tabbing is easy, until it isn't. Traditionally, using a spreadsheet has been the go-to option for smallish tournaments because, hey, you're pretty handy with Excel, right? Making draws in spreadsheets (or on paper) seems like a pretty approachable task; ultimately it's all cells and formulae and numbers unlike the more arcane underpinnings of actual tab software.

However, hand tabbing does require you to have a good working knowledge of how your format's rules work and how your spreadsheet software of choice can be made to work them. That process might be easy for you, or it might not be. But, either way, we'd like to think that Tabbycat offers a better alternative to hand-tabbing; regardless of how well you can actually hand-tab. The setup costs of creating a copy of Tabbycat are pretty low and you can speed through the process of draw creation, adjudicator allocation, and result entry at a pace. It's still not going to be as fast a spreadsheet for a small tournament, but we think it's getting pretty close. And in exchange for a little speed you get a much stronger guarantee of your draws being correct, options for online data entry, a more comprehensive and shareable final tab, and much more. Give it a shot!
