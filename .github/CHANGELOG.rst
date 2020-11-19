==========
Change Log
==========

2.5.0 (Nebelung)
----------------
*Release date: ?*

- Added URL field from the Room model to the Venues API endpoints as 'external URL'
- The Institution API endpoints show institutions' regions as their name, and regions can be created
- Added a preference to allow dedicated reply speaker. Thanks to Miha Frangež for the PR! (`#1584 <https://github.com/TabbycatDebate/tabbycat/issues/1584>`_)
- Adjudicator Feedback choices and draw flags are stored with PostgreSQL-specific arrays (`#1525 <https://github.com/TabbycatDebate/tabbycat/issues/1525>`_)
- Private URL submissions now store the participant whose link was used rather than just their IP address (`#1586 <https://github.com/TabbycatDebate/tabbycat/issues/1586>`_)
- Optimised database queries to create all debates in a draw at once (`#1376 <https://github.com/TabbycatDebate/tabbycat/pull/1376>`_)
- Optimised deletion of team private URLs (`#1618 <https://github.com/TabbycatDebate/tabbycat/pull/1618>`_)
- Reduced number of database queries in sending notifications (`#1592 <https://github.com/TabbycatDebate/tabbycat/pull/1592>`_)
- Fixed simulated annealing adjudicator allocator when initialised with the Hungarian method (`#1619 <https://github.com/TabbycatDebate/tabbycat/pull/1619>`_)
- Added selectors for adjudicator positions in draw emails (`#1423 <https://github.com/TabbycatDebate/tabbycat/pull/1423>`_)
- Implemented debate postponement, allowing debates to be marked as "postponed" in the results page. Postponed debates do not block draw generation, contrary to unconfirmed debates. (`#1563 <https://github.com/TabbycatDebate/tabbycat/pull/1563>`_)
- Added round weights so that team points can be pondered between rounds, implementing tapered scoring. Weights only affect the sum of team points. (`#1512 <https://github.com/TabbycatDebate/tabbycat/pull/1512>`_)
- Delegated the calculation of team and speaker rankings to database functions where available, with metrics using the same query. (`#1617 <https://github.com/TabbycatDebate/tabbycat/pull/1617>`_)
- Added in-context translation through Crowdin integration (`#1664 <https://github.com/TabbycatDebate/tabbycat/pull/1664>`_)
- Overhauled the results framework to allow for more types of ballots
    - BP finals now nominate only one team winning (`#527 <https://github.com/TabbycatDebate/tabbycat/issues/527>`_)
    - There are now settings to allow tied-point and low-point wins, with declared winners (`#643 <https://github.com/TabbycatDebate/tabbycat/issues/643>`_)
    - Two-team formats can now have scoreless ballots, and winner ballots are not restricted to elimination rounds (`#1003 <https://github.com/TabbycatDebate/tabbycat/issues/1003>`_)
    - Results are now discoverable through the API.
- Breaks are now explorable and manipulable through the API.
- Removed the simulated annealing adjudicator allocator.
- Fixed issue with Sentry integration preventing some debugging info from being included in error reports


2.4.7
-----
*Release date: 15 October 2020*

- Fixed draw display links not showing concurrent rounds (`#1239 <https://github.com/TabbycatDebate/tabbycat/issues/1239>`_)
- Record pages now show concurrent rounds
- Non-public speaker categories are now hidden from public API endpoints when unauthenticated


2.4.6
-----
*Release date: 19 September 2020*

- Fixed issue where team names with an institution were longer than the maximum size (`#1564 <https://github.com/TabbycatDebate/tabbycat/issues/1564>`_)
- Fixed issue that made saving motions impossible through the Round API detail endpoint
- Fixed issue that made filtering by source team impossible for the Feedback API


2.4.5
-----
*Release date: 19 July 2020*

- Fixed the display of room URLs on private URL pages (thanks Viran for the report)
- Preformed panels with a bracket range now sort more sensibly (thanks Zachary for the report)
- Fixed manual sorting of preformed panels in general
- Improved sorting of feedback table when sorting 'difference between base score and current score' (thanks Zachary for the report)
- Fixed issue where the last saved counter was not updating on normal tables


2.4.4
-----
*Release date: 13 July 2020*

- Fixed colours associated with adjudicators' scores not showing
- Showed validation errors when using API with invalid field names
- Prevented Tabbycat from creating default conflicts with the API if already specified in the request
- Fixed eligibility API endpoints when a list of participants is not present
- Fixed speaker category eligibility API endpoint not accepting speakers
- Allowed updating teams, excluding speakers, through the team detail API endpoint
- Added date and time formats for Malay


2.4.3
-----
*Release date: 4 July 2020*

- Fixed issue preventing break eligibility from saving (`#1521 <https://github.com/TabbycatDebate/tabbycat/issues/1521>`_)


2.4.2
-----
*Release date: 22 June 2020*

- Removed duplicate institution name in popovers (`#1515 <https://github.com/TabbycatDebate/tabbycat/issues/1515>`_)
- Fixed participant record page crashes resulting from `#1511 <https://github.com/TabbycatDebate/tabbycat/pull/1511>`_ (`#1518 <https://github.com/TabbycatDebate/tabbycat/pull/1518>`_)
- Fixed hanging in preformed panel creation


2.4.1
-----
*Release date: 21 June 2020*

- Fixed issue where redundant check-ins would crash (`#1513 <https://github.com/TabbycatDebate/tabbycat/pull/1513>`_)
- Require round sequence numbers to be nonnegative (`#1514 <https://github.com/TabbycatDebate/tabbycat/issues/1514>`_)
    - This change may cause upgrades of existing sites to fail with an ``IntegrityError`` if they have a negative round sequence number. Please change all round sequence numbers to positive numbers (or 0) before upgrading. Negative round numbers cause most Tabbycat pages to fail anyway, so functioning existing sites shouldn't have this problem.
- Adjust display of team names in registration cards (`#1511 <https://github.com/TabbycatDebate/tabbycat/pull/1511>`_)
- Fixed bug causing main action item not to appear in languages other than English
- Allowed null values for emoji and code names in Teams' API
- Enforced use of null values where field is undetermined yet cannot be blank in API
- Improved performance of certain database pages
- Fixed issue where null points caused an error in current standings
- Fixed issue preventing the creation of speakers in teams through API
- Little updates and clarifications to the documentation


2.4.0 (Manx)
------------
*Release date: 14 June 2020*

- Created an `application programming interface (API) <https://tabbycat.readthedocs.io/en/stable/features/api.html>`_ for most aspects of Tabbycat
- Filtered the home page for active tournaments with a new page to list inactive ones
- Added support for Simplified Chinese, Bengali, Malay, Russian, and shortened the language selector
- Renamed 'test score' to 'base score', as well as 'venue' to 'room'
- Deprecated and removed divisions-specific features
- Added a 'URL' field to Rooms. When a room is publicly displayed it will then present the nominated URL. This is designed so that you can more easily host online tournaments, but may also have use in other scenarios - e.g. linked to a per-room map.
- The 'Feedback explanation' preference now uses a full text area for easier text formatting
- Changing the sorting on debates in allocation views now only sorts once, so changing importances will no longer re-order the list immediately (`#1275 <https://github.com/TabbycatDebate/tabbycat/issues/1275>`_)
- Added room ranks to the Edit Adjudicator UI during elimination round, including sorting by room rank (`#1454 <https://github.com/TabbycatDebate/tabbycat/issues/1454>`_)
- Enabled debates to be sorted by the sum liveness of teams present
- Moved the 'Edit Database' menu item to the dropdown with the logo in the admin navigation
- Pull-ups can now be restricted to teams with the lowest draw strength (by speaker or team points) of their bracket
- Added team standing metrics: number of pull-ups, and draw strength by speaker score
- Extended draw strength so that it works for BP (`#1071 <https://github.com/TabbycatDebate/tabbycat/issues/1071>`_)
- Added the new emoji from Unicode 11 — thanks to Viran Weerasekera for this addition!
- Added toggle to hide adjudicators on the draw release page
- Separated private URL printing pages into teams and adjudicators
- Applied 'Show adjudicator institutions' preference to more cases; so if turned off, they should be hidden from public everywhere
- The Edit Venues screen now shows highlights for priority and venue category
- Tweaked the display of tables on mobile devices — they should now more reliably show a full BP draw without horizontal scrolling
- Grouped adjudicators by round when submitting feedback — reduce the length of the text shown in selector
- Fixed internal server error when standings precedence is empty (`#1108 <https://github.com/TabbycatDebate/tabbycat/issues/1108>`_)
- Fixed issue causing crashes when trainees were demoted after results were entered (`#922 <https://github.com/TabbycatDebate/tabbycat/issues/922>`_)
- Fixed issue where who-beat-whom would include elimination rounds (`#1073 <https://github.com/TabbycatDebate/tabbycat/issues/1073>`_)
- Fixed issue causing even panels to be missed for user warnings (`#1465 <https://github.com/TabbycatDebate/tabbycat/issues/1465>`_)
- Stopped actively maintaining `local installation instructions for Windows <https://tabbycat.readthedocs.io/en/latest/install/windows.html>`_


2.3.3
-----
*Release date: 26 April 2020*

- Fixed issue where the ballot graph would ignore draft ballots getting confirmed
- Fixed team draw notifications failing due to an unexpected variable
- Fixed ballot receipts not showing decimal speaker points
- Fixed issue where Docker installs would compile without css/javascript; breaking many pages


2.3.2
-----
*Release date: 19 October 2019*

- Fixed issue where teams would appear to be unavailable in break rounds
- Other minor fixes


2.3.1
-----
*Release date: 6 October 2019*

- Fixed issue where the institutions list would count teams/adjudicators outside of the tournament
- Fixed issue where a rejected ballot form would crash rather than providing an error message
- Fixed issue where the javascript bundle would not build on a local windows install
- Fixed issue where the adjudicator record pages would show an unreleased motion if that round's draw was released


2.3.0 (LaPerm)
--------------
*Release date: 27 September 2019*

- Added a preformed panel system which provides a powerful take on a 'shadow draw' workflow
    - Shadow draw systems allow an adjudication core to form panels prior to a round being drawn. For example, the panels for Round 4 could be formed while Round 3 is taking place. Most implementations do so by having the tab system create a copy of the Round 3 draw, form new panels on top of it, and then transpose these panels onto Round 4. In large tournaments this workflow allows an adjudication core much more time to consider panel formation
    - Tabbycat's preformed panels are formed per-round under a section available under the Setup menu. This interface looks like the standard Edit Adjudicators interface, but the 'debates' shown are based on a simulation of that round's results. These fake debates can then be prioritised
    - Adjudicators can then be allocated to those fake debates in order to create a pre-formed panel. When the real draw is ready to be created, the priority of each preformed panel will be matched to the priority of the real debates
    - By using the existing per-debate priority system, and by giving pre-formed panels their own priority, this workflow allows for very fine amounts of control over exactly how preformed panels are allocated as compared to a more simple top-down transposition of panels. Adjudication cores can easily target general areas of the draw (e.g. break-threshold brackets); control adjudicator strength within and across panels; and still account for special cases where a debate requires a particularly strong panel. At the same time, our existing options for automatic prioritisation and automatic allocation apply to all steps of this process so that preformed panels can be created and deployed rapidly
- Rewrote the Edit Adjudication, Venues, and Teams pages to enable a number of enhancements
    - These pages now live-update changes that were made on other instances of that page. As a result, users on different computers can each open the Edit Adjudicators page and see the changes made by the other users. This feature, along with sharding, should make it easier than ever to distribute the task of adjudicator allocation across an entire adjudication core
    - A new interface layout should better maximise space, particularly in BP settings, while also increasing the font size of key information
    - The unused panel is now able to sort adjudicators by name, score, or drag order
    - Average scores for all adjudicators, and a voting majority, are now shown next to the panel
    - Various allocation-relevant settings, such as the minimum feedback score needed for a voting position, are now available inline on the allocation page itself. This should enable much faster tweaks/iterations of these values
- The ballot entry page will now indicate which teams have currently or recently given 'iron person' speeches so that these can be easily tracked, audited, and confirmed. It does show by showing both a text-highlight/icon in the table and in a dedicated modal window. Thanks to Étienne Beaulé for contributing this feature!
- Split up the Django settings files. Note that this means if you are upgrading a local install of Tabbycat to this version you will need to:
    - Copy ``tabbycat/settings/local.example`` to become ``local.py`` (and fill in your original database details)
    - Optional: repeat the same copying procedure for ``development.example`` and set the ``LOCAL_DEVELOPMENT`` environmental variable to ``True`` if you would like to use the settings designed to aid local development
- A range of improvements to the email notifications contributed by Étienne Beaulé:
    - Ballot receipt emails now provide more information about team scores/points
    - Emails are now in a rich-text format
    - Custom emails may be sent out to select participants through the web-interface
    - Participants can be specifically included or excluded from receiving a notification before sending with checks for duplicate messages
    - Teams can be sent emails with their draw details
    - Emails can be tracked to determine if sent or read (SendGrid-specific)
- Expanded the use of private URLs (Encore Étienne Beaulé):
    - QR codes are now included in addition to the URL when printing private URLs
    - Private landing pages will now display check-in status (if check-ins are used) along with further details regarding break categories, regions, etc.
    - Current and former draw assignments will display along with submitted ballots (for adjudicators) on landing pages
- Reworked how conflicts are determined to support double-past institutional conflicts:
    - Added a "team-institution conflict" model
    - Like adjudicator-institution conflicts, team-institution conflicts are automatically created if you use the simple importer or the command-line importer; but if you edit the database, it's your responsibility to add/edit them
    - Institutional affiliations no longer matter for determining conflicts for either teams or adjudicators; only institutions listed in the team's or adjudicator's conflicts matter
    - An adjudicator/team now conflicts with an adjudicator if *any* institution appears as an institutional conflict for both parties
- When printing scoresheets you can now edit the motions display just on that printing page. This allows you to use placeholder motions in Tabbycat (in order to prevent leaks) while still producing ballots with the correct motions
- Tabbycat no longer tracks which round is the 'current' round and instead tracks the completion of individual rounds. This change does not alter any existing workflows, but makes it easier to run simultaneous draws in out-rounds
- Info-slides can now be split into paragraphs
- Check-in pages now differentiate between teams with 1 and 2 checked-in people in two-team formats
- Institutional caps in breaks can be based on the number of teams in the break. Thanks to Viran Weerasekera for this feature!
- Several Tabbycat functions, adjudicator/venue allocation and email notifications, have been shifted to worker processes to help make them more reliable. If you are upgrading a Tabbycat instance that you will continue to use for new tournaments you will need to install the Heroku toolbelt and run ``heroku ps:scale worker=1``
- Upgraded to Python 3.6, dropped support for Python 3.5 and below. Note that this will require you to upgrade your python versions if running locally.


2.2.10
------
*Release date: 10 February 2019*

- Fixed the display of feedback quantities on the Feedback Overview Page
- Fixed issue where 'ignored' feedback would hide the result from the feedback graph but not affect an adjudicator's current score. Thanks to Étienne for this fix


2.2.9
-----
*Release date: 24 January 2019*

- Fixed an issue that could cause errors for tournaments when using an atypical number of rounds and break sizes. Thanks to Étienne for this fix
- Fixed an issue where the display of adjudicator's record links would display their name twice


2.2.8
-----
*Release date: 14 December 2018*

- Fix issue where the check-in buttons were always disabled on admin and assistant pages
- Other minor fixes. Thanks to Étienne for these and for the check-in button fix!


2.2.7
-----
*Release date: 16 November 2018*

- Lock redis-py version to 2.10.6, as workaround for `compatibility issue between django-redis and redis-py <https://github.com/niwinz/django-redis/issues/342>`_
- Fix login link on page shown after a user logs out


2.2.6
-----
*Release date: 14 November 2018*

- Fix issue where check-ins could not be revoked
- Fix issue where the standings overview 'dashboard' included scores from elimination rounds. Thanks to Étienne for this fix
- Fix issue where the Average Individual Speaker Score metric would fail to calculate in some circumstances. Thanks to Étienne for this fix
- Fix issue where draw emails would crash if venues were unspecified. Thanks, again, to Étienne for this fix!


2.2.5
-----
*Release date: 21 October 2018*

- Remove the buttons from the public check-ins page (as these do nothing unless the user is logged in)
- Hopefully fixed error that could cause Team- and Adjudicator- Institutional conflicts to not show properly on Allocation pages
- Thanks to Étienne for pull requests fixing rare bugs in the user creation form and break generation when rounds are not present


2.2.4
-----
*Release date: 9 October 2018*

- Small fixes for functions related to email sending, conflict highlighting, and certain configurations of standings metrics


2.2.3
-----
*Release date: 28 September 2018*

- *Literally* fix the issue causing public views of released scoresheets to throw errors (thanks for the pull request Étienne)
- Fix minor spacing issues in printed ballots (thanks for the pull request Étienne)
- Fix issue where institution-less adjudicators would cause some draw views to crash (thanks for the pull request Étienne)


2.2.2
-----
*Release date: 22 September 2018*

- *Actually* fix the issue causing public views of released scoresheets to throw errors


2.2.1
-----
*Release date: 21 September 2018*

- Fix issue causing public views of released scoresheets to throw errors


2.2.0 (Khao Manee)
------------------
*Release date: 20 September 2018*

- Implemented a new server architecture on Heroku along with other optimisation that should significantly improve the performance of sites receiving lots of traffic. Note that if you are upgrading an existing Heroku instance this requires a few tweaks before you deploy the update:
    - Add the `https://github.com/heroku/heroku-buildpack-nginx.git` build pack under the Settings area of the Heroku Dashboard and positioning it first
    - If your Heroku Stack is not "heroku-16" (noted under that same Settings page) it will need to be set as such using the Heroku CLI and the ``heroku stack:set heroku-16 --app APP_NAME`` command
- Added a page to the documentation that details how to scale a Tabbycat site that is receiving large amounts of traffic; and another page that documents how to upgrade a Tabbycat site to a new version
- Added support for Japanese and Portuguese. Let us know if you'd like to help contribute translations for either language (or a new one)!
- The results-entry page now updates its data live, giving you a more up to date look at data entry progress and reducing the cases of old data leading people to enter new ballots when they meant to confirm them
- A huge thanks to Étienne Beaulé for contributing a number of major new features and bug fixes. Notably:
    - Added a means to mark feedback as 'ignored' so that it still is recorded as having been submitted, but does not affect the targeted-adjudicator's feedback score
    - Added email notification to adjudicators on round release
    - Implemented participant self-check-in through the use of their private URLs
    - Gave all participants to a tournament a private URL key rather than being by team, and added a landing page for the participants using this key
    - Implemented templated email notifications with ballot submission and round advance with the messages in a new settings panel. Private URL emails are now also customizable
    - Added the "average individual speaker score" metric which averages the scores of all substantive speeches by the team within preliminary rounds. The old "average speaker score" metric has been renamed to to "average total speaker score"
    - Reworked the ballots status graph to be an area chart
- Added the ability to hide motions on printed ballots (even if they have been entered). Thanks to Github user 0zlw for the feature request!
- Added the ability to unconfirm feedback from any of the views that show it
- BP motion statistics now also show average points split by bench and half
- Added a warning when users are close to their free-tier database limit on Heroku that makes it clear not to create new tournaments
- Added ``exportconfig`` and ``importconfig`` management commands to export and import tournament configurations to a JSON file
- Upgraded `django-dynamic-preferences <https://github.com/EliotBerriot/django-dynamic-preferences>`_ to version 1.6

  This won't affect most users, but advanced users previously having problems with a stray ``dynamic_preferences_users_userpreferencemodel`` table who are upgrading an existing instance may wish to run the SQL command ``DROP TABLE dynamic_preferences_users_userpreferencemodel;`` to remove this stray table. When this table was present, it caused an inconsistency between migration state and database schema that in turned caused the ``python manage.py flush`` command to fail. More information is available in the `django-dynamic-preferences changelog <https://django-dynamic-preferences.readthedocs.io/en/latest/history.html#migration-cleanup>`_


2.1.3
-----
*Release date: 21 August 2018*

- Added an alert for British Parliamentary format grand-final ballots that explains the workaround needed to nominate a sole winner
- Improved display of images shown when sharing Tabbycat links on social media
- Optimised the performance of several commonly-loaded pages. Thanks to Étienne Beaulé for the pull request!
- Prevented the entry of integer-scale feedback questions without the required min/max attributes
- Provided a shortcut link to editing a round's feedback weight
- Prevented standings from crashing when only a single standings metric is set


2.1.2
-----
*Release date: 14 July 2018*

- Fixed an error caused when calculating breaks including teams without institutions
- Improved display of long motions and info slides
- Fixed bug in feedback progress tracking with UADC-style adjudication
- Fixed bug where the public checks page would cause large amounts of failing requests
- Fixed visual issue with adjudicator lists wrapping poorly on mobile devices
- Limited the time it takes to serve requests to match Heroku's in-built limit; this may help improve the performance of sites under heavy load


2.1.1
-----
*Release date: 19 May 2018*

- The Scan Identifiers page now orders check-ins from top to bottom
- The Scan Identifiers now plays different sounds for failed check-ins
- The Scan Identifiers now has a toggle for sounds; allowing it to work in browsers like Safari that block auto-playing audio


2.1.0 (Japanese Bobtail)
------------------------
*Release date: 7 May 2018*

- Added an introductory modal for the adjudicator allocation page to help outline how the features and workflow operate
- Added an automated method for assigning importances to debates using their bracket or 'liveness'. This should allow smaller tournaments to more easily assign importances and save time for larger tournaments that do so
- Added the ability to switch between using 'team codes' and standard team names
    - By default team codes are set to match that team's emoji, but team codes are editable and can be imported like standard data
    - Team codes can be swapped in an out for standard team names at will, with precise control over the contexts in which either is used — i.e. in public-facing pages, in admin-facing pages, in tooltips, *etc.*
- Added a range of 'check-in' functionality
    - This includes barcode assignment, printing, and scanning. Scanning methods are optimised both for manual entry, entry with barcodes scanners, and for a 'live' scanning view that uses your phone's camera!
    - This includes new people and venue status pages that show an overview of check-in status and allow for easy manual check-ins; ideal for a roll-calls!. This page can also be made public
    - Ballot check-ins have been converted to this new method, and now all printed ballots will contain the barcodes needed to scan them
    - Venue check-ins have been added alongside the standard 'person' check-ins to allow you to track a room's status at the start of the day or round-by-round
- Added (partial) translations in French, Spanish and Arabic
    - Users can now use a link in the footer to switch the site's language into French, Spanish, or Arabic. By default Tabbycat should also match your browser's language and so automatically apply those languages if it matches
    - Our translations are generously provided by volunteers, but (so far) do not cover all of the interface text within Tabbycat. If you're interested in helping to translate new or existing languages please get in touch!
    - Thanks to the excellent team at QatarDebate for contributing the Arabic translations, and to Alejandro, Hernando, Julian and Zoe for contributing the Spanish translations.
- Added a new (beta) feature: allocation 'sharding'
    - Sharding allows you to split up the Adjudicator Allocation screen into a defined subset of the draw. This has been designed so that you can have multiple computers doing allocations simultaneously; allowing the adjudication core to split itself and tackle allocations in parallel.
    - Shards can be assigned into defined fractions (i.e. halves or fifths) according to specific criteria (i.e. bracket or priority) and following either a top-to-bottom sorting or a mixed sorting that ensures each bracket has an even proportion of each criteria.
- Added an option to show a "Confirm Digits" option to pre-printed ballots that asks adjudicators to confirm their scores in a manner that may help clarify instances or bad handwriting. This can be enabled in the "Data Entry" settings area.
- Added a 'liveness' calculator for BP that will estimate whether each team has, can, or can't break in each of their categories (as previously existed for 2-team formats)
- Added draw pull-up option: pull up from middle
- Added new draw option: choose pull-up from teams who have been pulled up the fewest times so far
- Added the ability to have different 'ballots-per-debates' for in/out rounds; accommodating tournaments like Australian Easters that use consensus for preliminary rounds but voting for elimination rounds.
- Added time zone support to the locations where times are displayed
- Administrators can now view pages as if they were Assistants; allowing them to (for example) use the data entry forms that enforce double-checking without needed to create a separate account
- Fixed χ² test in motion statistics, and refactored the motion statistics page
- Teams, like adjudicators, no longer need to have an institution
- Added a page allowing for bulk updates to adjudicator scores
- Added break categories to team standings, and new team standings pages for break categories
- Made speaker standings more configurable
    - Second-order metrics can now be specified
    - Added trimmed mean (also known as high-low drop)
    - Added ability to set no limit for number of missed debates
    - Standard deviation is now the population standard deviation (was previously sample), and
      ranks in ascending order if used to rank speakers.
- Quality of life improvements
    - Added a "☆" indicator to more obviously liveness in the adjudicator allocation screen
    - Added WYSIWYG editor for tournament welcome message, and moved it to tournament configuration
    - Added "appellant" and "respondent" to the side name options
    - Added a two new columns to the feedback overview page: one that displays the current difference between an adjudicator's test score and their current weighted score; another the displays the standard deviation of an adjudicator's feedback scores
    - Added an 'important feedback' page that highlights feedback significantly above or below an adjudicator's test score
    - Added a means to bulk-import adjudicator scores (for example from a CSV) to make it easier to work with external feedback processing
    - Speakers and speaker's emails in the simple importer can now be separated by commas or tabs in addition to new lines
    - The "shared" checkbox in the simple importer is now hidden unless the relevant tournament option is enabled
    - Current team standings page now shows silent round results if "Release all round results to public" is set
    - The Consensus vs Voting options for how ballots work has now been split into two settings: one option for preliminary rounds and one option for elimination rounds
    - Speaker scores now show as integers (without decimals) where the tournament format would not allow decimals
    - Added a page showing a list of institutions in the tournament
    - On the assistant "enter results" page, pressing "/" jumps to the "Find in Table" box, so data entry can be done entirely from your keyboard
- Switched to using a Websockets/Channels based infrastructure to better allow for asynchronous updates. This should also ameliorate cases where the Memcachier plugin expired due to inactivity which would then crash a site. Notes for those upgrading:
    - On Heroku: You should remove the Memcachier plugin and instead add 'heroku-redis' to any instances being upgraded
    - Locally: You should recreate your `local_settings.py` from the `local_settings.example` file
- Upgraded to Django 2.0
    - Converted most raw SQL queries to use the new ``filter`` keyword in annotations


2.0.7
-----
*Release date: 13 April 2018*

- Fixed an issue preventing draws with pre-allocate sides generating


2.0.6
-----
*Release date: 20 March 2018*

- Added reminder to add own-institution conflicts in the Edit Database area
- Other minor fixes


2.0.5
-----
*Release date: 7 February 2018*

- Improved the printing of scoresheets and feedback forms on Chrome.
- Other minor fixes


2.0.4
-----
*Release date: 22 January 2018*

- Add alert for users who try to do voting ballots on BP-configured tournaments
- Fixed issue where draws of the "manual" type would not generate correctly
- Fixed issue where a ballot's speaker names dropdown would contain both team's speakers when using formats with side selection
- Fixed issue where scoresheets would not show correctly under some configurations
- Improved display of really long motions when using the inbuilt motion-showing page
- Other minor fixes


2.0.3
-----
*Release date: 3 December 2017*

- Fixed issue where the 'prefix team name with institution name' checkbox would not be correctly saved when using the Simple Importer
- Removed the scroll speed / text size buttons on mobile draw views that were making it difficult to view the table
- Improved the display of the motions tab page on mobile devices and fixed an issue where it appeared as if only half the vetoes were made


2.0.2
-----
*Release date: 27 November 2017*

- Fixes and improvements to diversity overview
    - Fixed average feedback rating from teams, it was previously (incorrectly) showing the average feedback rating from all adjudicators
    - Gender splits for average feedback rating now go by target adjudicator; this was previously source adjudicator
    - Persons with unknown gender are now shown in counts (but not score/rating averages); a bug had previously caused them to be incorrectly counted as zero
    - Improved query efficiency of the page
- Improved the BP motions tab for out-rounds by specifying advancing teams as "top/bottom ½" rather than as 1st/4th and removed the average-points-per-position graphs that were misleading
- Improved handling of long motions in the motion display interface
- Fixed issue where creating BP tournaments using the wizard would create an extra break round given the size of the break specified
- Fixed auto-allocation in consensus panels where there are fewer judges than debates in the round
- Fixed reply speaker validity check when speeches are marked as duplicate
- Prohibit assignment of teams to break categories of other tournaments in Edit Database area


2.0.1
-----
*Release date: 21 November 2017*

- Fixed issue where results submission would crash if sides are unconfirmed
- Fixed issue where scoresheets would not display properly for adjudicators who lack institutions
- Fixed issue where the round history indicators in the Edit Adjudicators page would sometimes omit the "rounds ago" indicator


2.0.0 (Iberian Lynx)
--------------------
*Release date: 13 November 2017*

- British Parliamentary support
    - Full support for British Parliamentary format has been added and we're incredibly excited to see Tabbycat's unique features and design (finally) available as an option for those tabbing in the predominant global format
    - As part of the implementation of this format we've made significant improvements over existing tab software on how sides are allocated within BP draws. This means that teams are less likely to have 'imbalanced' proportions of side allocations (for example having many more debates as Opening Government than Closing Opposition)
    - We've added a new "Comparisons" page added to the documentation to outline some of the key differences between Tabbycat and other software in the context of BP tabbing
- Refreshed interface design
    - The basic graphic elements of Tabbycat have had a their typography, icons,  colours, forms, and more redesign for a more distinctive and clear look. We also now have an official logo!
    - The "Motions" stage of the per-round workflow has now been rolled into the Display area to better accommodate BP formats and consolidate the Draw/Motion 'release' process
    - Sidebar menu items now display all sub-items within a section, such as for Feedback, Standings, and Breaks
    - Better tablet and mobile interfaces; including a fully responsive sidebar for the admin area that maximises the content area
    - More explicit and obvious calls-to-action for the key tasks necessary to running a round, with better interface alerts and text to help users understand when and why to perform crucial actions
    - Redesigned motions tab page that gives a better idea of the sample size and distribution of results in both two- and four- team formats
- Improved handling of Break Rounds ballots and sides allocation
    - The positions of teams within a break round are now created by the initial draw generation in an 'unset' state in recognition that most tournaments assign these manually (through say a coin toss). This should help clarify when showing break rounds draws when sides are or are not finalised
    - Break rounds ballots for formats where scores are not typically entered (i.e. BP) will only specify that you nominate the teams advancing rather than enter in all of the speakers' scores
- Now, like Break Categories, you can define arbitrary Categories such as 'Novice' or 'ESL' to create custom Speaker tabs for groups of Speakers
- You can now release an Adjudicators Tab showing test scores, final scores, and/or per-round feedback averages
- Information Slides can now be added to the system; either for showing to an auditorium within Tabbycat or for displaying alongside the public list of motions and/or the motions tab
- Teams and adjudicators are no longer required to have institutions; something that should be very useful when setting up small IVs and the like
- Private URLs can now be incrementally generated. Records of sent mail are now also kept by Tabbycat, so that emails can be incrementally sent to participants as registration data changes
- Quality of life improvements
    - After creating a new tournament you will now be prompted to apply a basic rules and public information preset
    - Better handling of errors that arise when a debate team is missing or where two teams have been assigned the same side
    - Fixed issue where the adjudicator feedback graphs would not sort along with their table
    - The Feedback Overview page now makes it more clear how the score is determined, the current distribution of scores, and how scores affect the distribution of chairs, panellists, and trainees
    - Speaker tabs now default to sorting by average, except for formats where we are certain that they must be sorted by total. The speaker tab page itself now prominently notes which setting is is currently using
    - 'Feedback paths' now default to a more permissive setting (rather than only allowing Chairs to submit feedback) and the Feedback Overview page will note that current configuration
    - Emails can be assigned to adjudicators and teams in the Simple Importer
    - More of the tables that allow you to set or edit data (such as the check-in tables for adjudicators, teams and venues) now automatically save changes
    - When adding/editing users extraneous fields have been hidden and the "Staff" and "Superuser" roles have new sub-text clarifying what they mean for users with those permissions
    - Team record pages now show cumulative team points, and if the speaker tab is fully released, speaker scores for that team in each debate


1.4.6
-----
*Release date: 23 October 2017*

- Fixed issue where speaker standings with a large amount of non-ranking speakers would cause the page to load slowly or time-out.


1.4.5
-----
*Release date: 14 October 2017*

- Added warning message when adjudicator scores are outside the expected range
- Fixed handling of uniqueness failure in simple importer for teams


1.4.4
-----
*Release date: 27 September 2017*

- Fixed Vue dependency issue preventing Heroku installs after a dependency release
- Fixed issue with formatting non-numeric standings metrics
- Fixed behaviour of public tabs when all rounds are silent


1.4.3
-----
*Release date: 9 September 2017*

- A number of improvements to error handling and logging
- Changed the "previous round" of an elimination round to point to the last one in the same break category
- Other minor bug fixes


1.4.2
-----
*Release date: 23 August 2017*

- Minor bug fixes and error logging improvements


1.4.1
-----
*Release date: 2 August 2017*

- Fixed bug that prevented edited matchups from being saved
- Added flag to prevent retired sites from using the database for sessions


1.4.0 (Havana Brown)
--------------------
*Release date: 26 July 2017*

- Overhauled the adjudicator allocation, venue allocation, and matchups editing pages, including:
    - Upgraded to Vue 2.0 and refactored the code so that each page better shares methods for displaying the draw, showing additional information, and dragging/dropping
    - When dragging/dropping, the changed elements now 'lock' in place to indicate that their saving is in-progress
    - Added conflicts and recent histories to the slideovers shown for teams/adjudicators
    - Added 'ranking' toggles to visibly highlight adjudicator strengths and more easily identify unbalanced panels
    - Each interface's table is now sortable by a debate's importance, bracket, liveness, etc.
- Added a new "Tournament Logistics" guide to the documentation that outlines some general best practices for tabbing tournaments. Thanks to Viran Weerasekera, Valerie Tierney, Molly Dale, Madeline Schultz, and Vail Bromberger for contributing to this document
- Added (basic) support for the Canadian Parliamentary format by allowing for consensus ballots and providing a preset. However note that only some of the common draw rules are supported (check our documentation for more information)
- Added an ESL/EFL tab release option and status field
- Added a chi-squared test to measure motion balance in the motion standings/balance. Thanks to Viran Weerasekera for contributing this
- The Auto Allocate function for adjudicators will now also allocate trainees to solo-chaired debates
- Added a 'Tab Release' preset for easily releasing all standings/results pages after a tournament is finished
- Added 'Average Speaks by Round' to the standings overview page
- Fixed issue where the Auto Allocator was forming panels of incorrect strengths in debates identified as less important
- Fixed issue where toggling iron-person speeches on and off wouldn't hide/unset the relevant checkboxes
- Fixed issue where VenueCategories could not be edited if they did not have Venues set
- Various other small fixes and improvements


1.3.1
-----
*Release date: 26 May 2017*

- Fixed bug that allowed duplicate emoji to be occasionally generated


1.3.0 (Genetta)
---------------
*Release date: 9 May 2017*

- Added the ability to mark speeches as duplicates when entering ballots so that they will not show in speaker tabs, intended for use with 'iron-man' speeches and swing speakers
- Reworked venue constraints and venue display options by streamlining "venue groups" and "venue constraint categories" into a single "venue category" type, with options for how they are used and displayed
- Relocated the Random (now renamed 'Private') URL pages to the Setup section and added pages for printing/emailing out the ballot submission URLs
- Reworked the simple data importer (formerly the visual importer) to improve its robustness
- Improved guards against having no current round set, and added a new page for manually overriding the current round (under Configuration)
- Added a preference for controlling whether assistant users have access to pages that can reveal draw or motions information ahead of their public release
- Added the ability to limit tab releases to a given number of ranks (*i.e.* only show the top 10 speakers)
- Added the ability to redact individual person's identifying details from speaker tabs
- Added the ability for user passwords to be easily reset
- Added a minimal set of default feedback questions to newly created Tournaments
- When a tournament's current round is set, redirect to a page where it can be set, rather than crashing
- A number of other minor bug fixes and enhancements


1.2.3
-----
*Release date: 17 March 2017*

- Improved the display of the admin ballot entry form on mobile devices
- A number of other minor bug fixes


1.2.2
-----
*Release date: 4 March 2017*

- Protected debate-team objects from cascaded deletion, and added warning messages with guidance when users would otherwise do this
- A number of other minor bug fixes


1.2.1
-----
*Release date: 25 February 2017*

- Printable feedback forms will now display the default rating scale, any configured introduction text, and better prompt you to add additional questions
- A number of other minor bug fixes


1.2.0 (Foldex)
--------------
*Release date: 15 February 2017*

- Changed the core workflow by splitting display- and motion- related activities into separate pages to simplify each stage of running a round
- Added support for Docker-based installations to make local/offline installations much more simple
- Added a "Tabbykitten" version of Tabbycat that can be deployed to Heroku without a needing a credit/debit card
- Added button to load a demo tournament on the 'New Tournament' page so it is easier to test-run Tabbycat
- Changed venue groups to be separate to venue constraint categories
- Modified the licence to clarify that donations are required for some tournaments and added a more explicit donations link and explanation page
- Added information about autosave status to the adjudicator allocations page
- Added configurable side names so that tournaments can use labels like "Proposition"/"Opposition" instead of "Affirmative"/"Negative"
- Started work on basic infrastructure for translations


1.1.7
-----
*Release date: 31 January 2017*

- Yet more minor bug fixes
- The auto-allocation UI will now detail your minimum rating setting better
- Added guidance on database backups to documentation


1.1.6
-----
*Release date: 19 January 2017*

- A number of minor bug fixes
- Added basic infrastructure for creating tabbycat translations


1.1.5
-----
*Release date: 12 January 2017*

- A number of minor bug fixes and improvements to documentation


1.1.4
-----
*Release date: 25 November 2016*

- Redesigned the footer area to better describe Tabbycat and to promote donations and related projects
- Slight tweaks to the site homepage and main menus to better accommodate the login/log out links
- A few minor bug fixes and improvements to error reporting


1.1.3
-----
*Release date: 15 September 2016*

- Fixed bug affecting some migrations from earlier versions
- Made latest results show question mark rather than crash if a team is missing
- Fixed bug affecting the ability to save motions
- Fixed bug preventing draw flags from being displayed


1.1.2
-----
*Release date: 14 September 2016*

- Allow panels with even number of adjudicators (with warnings), by giving chair the casting vote
- Removed defunct person check-in, which hasn't been used since 2010
- Collapsed availability database models into a single model with Django content types
- Collapsed optional fields in action log entries into a single generic field using Django content types
- Added better warnings when attempting to create an elimination round draw with fewer than two teams
- Added warnings in Edit Database view when editing debate teams
- Renamed "AIDA pre-2015" break rule to "AIDA 1996"


1.1.1
-----
*Release date: 8 September 2016*

- Fixed a bug where the team standings and team tab would crash when some emoji were not set


1.1.0 (Egyptian Mau)
--------------------
*Release date: 3 September 2016*

- Added support for the United Asian Debating Championships style
- Added support for the World Schools Debating Championships style
- Made Windows 8+ Emoji more colourful
- Fixed an incompatability between Vue and IE 10-11 which caused tables to not render
- Minor bug fixes and dependency updates


1.0.1
-----
*Release date: 19 August 2016*

- Fixed a minor bug with the visual importer affecting similarly named institutions
- Fixed error message when user tries to auto-allocate adjudicators on unconfirmed or released draw
- Minor docs edits


1.0.0 (Devon Rex)
-----------------
*Release date: 16 August 2016*

Redesigned and redeveloped adjudicator allocation page
  - Redesigned interface, featuring clearer displays of conflict and diversity information
  - Changes to importances and panels are now automatically saved
  - Added debate "liveness" to help identify critical rooms—many thanks to Thevesh Theva
  - Panel score calculations performed live to show strength of voting majorities
New features
  - Added record pages for teams and adjudicators
  - Added a diversity tab to display demographic information about participants and scoring
Significant general improvements
  - Shifted most table rendering to Vue.js to improve performance and design
  - Drastically reduced number of SQL queries in large tables, *e.g.* draw, results, tab
Break round management
  - Completed support for break round draws
  - Simplified procedure for adding remarks to teams and updating break
  - Reworked break generation code to be class-based, to improve future extensibility
  - Added support for break qualification rules: AIDA Australs, AIDA Easters, WADL
Feedback
  - Changed Boolean fields in AdjudicatorFeedbackQuestion to reflect what they actually do
  - Changed "panellist feedback enabled" option to "feedback paths", a choice of three options

- Dropped "/t/" from tournament URLs and moved "/admin/" to "/database/", with 301 redirects
- Added basic code linting to the continuous integration tests
- Many other small bug fixes, refactors, optimisations, and documentation updates


0.9.0 (Chartreux)
-----------------
*Release date: 13 June 2016*

- Added a beta implementation of the break rounds workflow
- Added venue constraints, to allow participants or divisions to preferentially be given venues from predefined groups
- Added a button to regenerate draws
- Refactored speaker standings implementation to match team standings implementation
- New standings metrics, draw methods, and interface settings for running small tournaments and division-based tournaments
- Improved support for multiple tournaments
- Improved user-facing error messages in some scenarios
- Most frontend dependencies now handled by Bower
- Static file compilation now handled by Gulp
- Various bug fixes, optimisations, and documentation edits


0.8.3
-----
*Release date: 4 April 2016*

- Restored and reworking printing functionality for scoresheets/feedback
- Restored Edit Venues and Edit Matchups on the draw pages
- Reworked tournament data importers to use csv.DictReader, so that column order in files doesn't matter
- Improved dashboard and feedback graphs
- Add separate pro speakers tab
- Various bug fixes, optimisations, and documentation edits


0.8.2
-----
*Release date: 20 March 2016*

- Fixed issue where scores from individual ballots would be deleted when any other panel in the round was edited
- Fixed issue where page crashes for URLs with "tab" in it but that aren't recognized tab pages


0.8.1
-----
*Release date: 15 March 2016*

- Fixed a bug where editing a Team in the admin section could cause an error
- Added instructions on how to account for speakers speaking twice to docs
- Venues Importer wont show VenueGroup import info unless that option is enabled


0.8.0 (Bengal)
--------------
*Release date: 29 February 2016*

- Upgraded to Python 3.4, dropped support for Python 2
- Restructured directories and, as a consequence, changed database schema
- Added Django migrations to the release (they were previously generated by the user)
- Migrated documentation to `Read The Docs <http://tabbycat.readthedocs.io>`_
- New user interface design and workflow
- Overhauled tournament preferences to use `django-dynamic-preferences <https://github.com/EliotBerriot/django-dynamic-preferences>`_
- Added new visual data importer
- Improved flexibility of team standings rules
- Moved data utility scripts to Django management commands
- Changed emoji to Unicode characters
- Various other fixes and refinements


0.7.0 (Abyssinian)
------------------
*Release date: 31 July 2015*

- Support for multiple tournaments
- Improved and extensible tournament data importer
- Display gender, region, and break category in adjudicator allocation
- New views for online adjudicator feedback
- Customisable adjudicator feedback forms
- Randomised URLs for public submission
- Customisable break categories
- Computerised break generation (break round draws not supported)
- Lots of fixes, interface touch-ups and performance enhancements
- Now requires Django 1.8 (and other package upgrades)
