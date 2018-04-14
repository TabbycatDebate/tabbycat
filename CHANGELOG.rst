==========
Change Log
==========

2.1.0 (Japanese Bobtail)
------------------------
*Release date: TBA*

- Added an introductory modal for the Edit Adjudicators interface to help outline how the workflow operates
- Added an automated method for assigning importances to debates using their bracket or 'liveness'. This should allow smaller tournaments to more easily assign importances and save time for larger tournaments that do so
- Added the ability to switch between using 'team codes' and standard team names
    - By default team codes are set to match that team's emoji, but team codes are editable and can be imported like standard data
    - Team codes can be swapped in an out for standard team names at will, with precise control over the contexts in which either is used — i.e. in public-facing pages, in admin-facing pages, in tooltips, etc/
- Added a range of 'check-in' functionality
    - This includes barcode assignment, printing, and scanning. Scanning methods are optimised both for manual entry, entry with barcodes scanners, and for a 'live' scanning view that uses your phone's camera!
    - This includes new people and venue status pages that show an overview of check-in status and allow for easy manual check-ins; ideal for a roll-calls!. This page can also be made public
    - Ballot check-ins have been converted to this new method, and now all printed ballots will contain the barcodes needed to scan them
    - Venue check-ins have been added alongside the standard 'person' check-ins to allow you to track a room's status at the start of the day or round-by-round
- Added (partial) translation support
    - Users can now use a button in the footer to switch the site's language into French, Spanish, or Arabic. By default Tabbycat should also match your browser's language and so automatically apply those languages if it matches.
    - Our translations are generously provided by volunteers, but (so far) do not cover all of the interface text within Tabbycat. If you were interested in helping to translate new or existing languages please get in touch!
- Added a new (beta) feature: allocation 'sharding'
    - Sharding allows you to split up the Adjudicator Allocation screen into a defined subset of the draw. This has been designed so that you can have multiple computers doing allocations simultaneously; allowing the adjudication core to split itself and tackle allocations in parallel.
    - Shards can be assigned into defined fractions (i.e. halves or fiths) according to specific criteria (i.e. bracket or priority) and following either a top-to-bottom sorting or a mixed sorting that ensures each bracket has an even proportion of each criteria.
- Added draw pull-up option: pull up from middle
- Added new draw option: choose pull-up from teams who have been pulled up the fewest times so far
- Added the ability to have different 'ballots-per-debates' for in/out rounds; accommodating tournaments like Australian Easters that use consensus for preliminary rounds but voting for elimination rounds.
- Added time zone support to the locations where times are displayed
- Administrators can now view pages as if they were Assistants; allowing them to (for example) use the data entry forms that enforce double-checking without needed to create a separate account
- Fixed χ² test in motion statistics, and refactored and moved motion statistics page
- Teams, like adjudicators, no longer need to have an institution
- Added page allowing update of adjudicator scores in bulk
- Made speaker standings more configurable
    - Second-order metrics can now be specified
    - Added trimmed mean (also known as high-low drop)
    - Added ability to set no limit for number of missed debates
    - Standard deviation is now the population standard deviation (was previously sample), and
      ranks in ascending order if used to rank speakers.
- Quality of life improvements
    - Added a 'liveness' calculator for BP
    - Added a "☆" indicator to more obviously liveness in the edit adjudicators screen
    - Added WYSIWYG editor for tournament welcome message, and moved it to tournament configuration
    - Added "appellant" and "respondent" to the side name options
    - Added a column to the feedback overview page that displays the current difference between an adjudicator's test score and current weighted score
    - Added an 'important feedback' page that highlights feedback significantly above or below an adjudicator's test score
    - Added a means to bulk-import adjudicator scores (for example from a CSV) to make it easier to work with external feedback processing
    - Speakers and speaker's emails in the simple importer can now be separated by commas or tabs in addition to new lines
    - The "shared" checkbox in the simple importer is now hidden unless the relevant tournament option is enabled
    - Current team standings page now shows silent round results if "Release all round results to public" is set
    - The Consensus vs Voting options for how ballots work has not been split into two settings: one for preliminary rounds and one for elimination rounds
    - Speaker scores now show as integers (without decimals) where the tournament format would not allow decimals.
    - Added a page showing a list of institutions in the tournament
- Switched to using a Websockets/Channels based infrastructure to better allow for asynchronous updates. This should also ameliorate cases where the memcachier plugin expired due to inactivity which would then crash a site. Notes for those upgrading:
    - On Heroku: You should remove the memcachier plugin and instead add 'heroku-redis' to any instances being upgraded
    - Locally: You should recreate your local_settings.py from the example file
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
    - Redesigned motions tab page that gives a better idea of the sample size and distribution of results in both two- and three- team formats
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

