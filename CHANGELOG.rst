==========
Change Log
==========

1.3.0
-----
*Release date: TBC*

- Added the ability to mark speeches as duplicates when entering ballots so that they will not show in speaker tabs. This should make dealing with 'Iron Man' speeches and swing speakers much easier.
- Reworked the venue constraints system and venue display options by removing Venue Groups and Venue Constraint Categories in favour of Venue Categories, Venue Constraints, and new options for configuring how a given category affects how a venue is named in the draw.
- Added a preference for controlling whether assistant users have access to pages that can reveal draw or motions information ahead of their public release
- Added the ability to limit tab releases to a given number of ranks (ie only show the top 10 speakers)
- Added the ability to redact individual person's identifying details from speaker tabs
- Added the ability for user passwords to be easily reset
- Added a minimal set of default questions to newly created Tournaments.


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
- Slight tweaks to the site homepage and main menus to better accomodate the login/log out links
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

