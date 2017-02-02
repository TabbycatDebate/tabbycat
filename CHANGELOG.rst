==========
Change Log
==========


1.2.0
-----
- Redesigned the core round workflow; splitting of the "Display Draw" and "Motions" actions into separate pages to make for a more streamlined user experience
- Added information about autosave status to the Allocations page
- Added basic infrastructure for creating tabbycat translations
- Added the ability to import 'demo' data when creating a new tournament


1.1.7
-----
- Yet more minor bug fixes
- The auto-allocation UI will now detail your minimum rating setting better


1.1.6
-----
- A number of minor bug fixes
- Added basic infrastructure for creating tabbycat translations


1.1.5
-----
- A number of minor bug fixes and improvements to documentation


1.1.4
-----

- Redesigned the footer area to better describe Tabbycat and to promote donations and related projects
- Slight tweaks to the site homepage and main menus to better accomodate the login/log out links
- A few minor bug fixes and improvements to error reporting


1.1.3
-----

- Fixed bug affecting some migrations from earlier versions
- Made latest results show question mark rather than crash if a team is missing
- Fixed bug affecting the ability to save motions
- Fixed bug preventing draw flags from being displayed


1.1.2
-----

- Allow panels with even number of adjudicators (with warnings), by giving chair the casting vote
- Removed defunct person check-in, which hasn't been used since 2010
- Collapsed availability database models into a single model with Django content types
- Collapsed optional fields in action log entries into a single generic field using Django content types
- Added better warnings when attempting to create an elimination round draw with fewer than two teams
- Added warnings in Edit Database view when editing debate teams
- Renamed "AIDA pre-2015" break rule to "AIDA 1996"


1.1.1
-----

- Fixed a bug where the team standings and team tab would crash when some emoji were not set


1.1.0 (Egyptian Mau)
--------------------

- Added support for the United Asian Debating Championships style
- Added support for the World Schools Debating Championships style
- Made Windows 8+ Emoji more colourful
- Fixed an incompatability between Vue and IE 10-11 which caused tables to not render
- Minor bug fixes and dependency updates


1.0.1
-----

- Fixed a minor bug with the visual importer affecting similarly named institutions
- Fixed error message when user tries to auto-allocate adjudicators on unconfirmed or released draw
- Minor docs edits


1.0.0 (Devon Rex)
-----------------
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
- Restored and reworking printing functionality for scoresheets/feedback
- Restored Edit Venues and Edit Matchups on the draw pages
- Reworked tournament data importers to use csv.DictReader, so that column order in files doesn't matter
- Improved dashboard and feedback graphs
- Add separate pro speakers tab
- Various bug fixes, optimisations, and documentation edits


0.8.2
-----
- Fixed issue where scores from individual ballots would be deleted when any other panel in the round was edited
- Fixed issue where page crashes for URLs with "tab" in it but that aren't recognized tab pages


0.8.1
-----

- Fixed a bug where editing a Team in the admin section could cause an error
- Added instructions on how to account for speakers speaking twice to docs
- Venues Importer wont show VenueGroup import info unless that option is enabled


0.8.0 (Bengal)
--------------

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

