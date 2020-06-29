.. tournament-logistics:

====================
Tournament Logistics
====================

Unlike the rest of our documentation, this section does not deal with particular features or technical concerns with Tabbycat itself. Instead it is an attempt to outline the logistics of tab direction and aims to be of general relevance for people running major tournaments. At present, it is organised by the various ‘stages' of tabbing a tournament, and most of the content takes the form of check-lists or comments designed to highlight and provide guidance on common issues.

Whilst it aims for general relevance, we should note that this guide is relatively opinionated and mostly written from the perspective of people whose primary experience is tabbing at Australasian tournaments using Tabbycat. That said, we welcome feedback and additions that can account for different format and regional considerations. In the future, if the guide becomes more general and more extensive, it could be spun off into a separate project.

.. note:: As with the rest of our documentation, this page is source-available and we welcome :ref:`feedback and contributions <contributing>`. Note also that we've formatted this guide a single page to reduce clutter, but the sub-sections in the sidebar can be used to help navigate across sections.

Planning and Preparation
========================

This section aims to outline concerns that occur in the months before the tournament: after you have agreed to help with tabbing and while the organising committee and adjudication core are deciding how they want to run key processes such as registration and feedback. It is organised in terms of who you should coordinate with in order to plan for a well-tabbed tournament.

General Notes
-------------

You should avoid being the sole person responsible for that tab unless it is a small tournament. There are many cases where you want to be in several places at once and the easiest way to accommodate that is by having co-directors or trusted assistants. Few tab decisions require a single source of authority; it is far better to have multiple people available to share responsibilities around.

In a similar manner, it is worth considering how you can use the tournament to help train other people. Typically, knowledge of tabbing is concentrated in relatively few people and gained mostly through on-the-ground experience; meaning that every tournament should be approached as rare opportunity to help spread knowledge about tabbing more widely in a circuit. Consider reaching out to institutions or the tournament as a whole to see if they have anyone who would be interested in helping out.

Convenors
---------

It might sound obvious but it will pay to have a very thorough conversation about the tab process (more or less the contents of this document) with the convenors a few months out from the tournament. Do this even if you know the convenors to be knowledgeable or experienced debaters. Key concerns are:

.. rst-class:: spaced-list

- Whether internet access will be available and whether participants can be presumed to have smart phones. This has an obvious impact on how online feedback, ballots, and draw release is done. Note that Eduroam is not necessarily a reliable guarantee of access; many participants will come from universities who don't have access to it or will need to follow a setup process that is onerous or requires them to be at their home institution.
- What kind of room is the tab room going to be? Is it possible to optimize its placement when the bookings for rooms are made? Key details include: How large is it? Does it have a sufficient amount of desk space (for data entry)? Does it have a good projector (for allocations)?
- If they have the resources, having an adjacent room available for just the adjudication core to use can also be useful. While you want to work closely with the adjudication core, they may want to discuss sensitive information (motions, equity) in a space without volunteers present; or they might at times get in the way of things, such as by eating lunch in the middle of a frenetic ballot entry process.
- Ensure that plans are made for food to be brought to tab room. Otherwise you will starve and the adjudication core will swan off to lunch. Having regular access to caffeine can also be similarly essential to some adjudication and tab teams.
- What kind of printers will be available? Can the tournament buy/borrow one? This is obviously a key consideration for pre-printed ballots. Also try and ensure there are back-up printing options if possible. Clearly stipulate your need for ink and paper; and try and opt for a black/white laserjet, over an inkjet, if possible.
- What kind of volunteers will be available? How many, and what is their experience level? As a very broad recommendation, you probably want around 1 volunteer for every 10 rooms, assuming volunteers are performing a dual role as data-enterers and ballot-collectors.
- Will the tournament make a donation to whoever maintains the tabbing software you are using? Depending on the license of your tabbing software and the nature of your tournament (for profit vs not for profit) this may be required. Also, if your tab is self-hosted or independently hosted (such as how Tabbycat is generally deployed on Heroku) accounting officers should also be aware that there will be some costs associated with hosting the tab.
- You should also ensure that people helping with the tab are fairly compensated for their flights, registration, etc and that any volunteers are invited along to socials and/or given some other recompense.
- Will Swing teams be available? You should plan to have at least one more than you need. For example, with 39 teams, you should have both an 40th swing team to fill in the draw, and the option to easily assemble an 41st swing team in case a team goes missing. At very large tournaments (say over 150 teams) you should plan for even more swing team capacity — it's not unheard of for say three teams to vanish all in a single round. In these cases, you should try and ensure that the swing teams are always ready to go — i.e. that that they are pre-formed, you have a clear communication channel with them, and that they distributed/waiting near the debating rooms so they can fill in at a moment's notice (often you will only find out that teams are missing right as debates are scheduled to start).
- How will critical information be communicated to participants? Consider that in general, Facebook announcements do not reach many people, although paying to boost the posts is often a very cheap way of dramatically raising their effectiveness. In particular also ensure or check how you manage to get in touch with teams or adjudicators who go missing: will they have reliable phone numbers? Can you get a list of institutional reps who can be reliably called? You want to have processes in place for chasing up adjudicators who do things such as make scoring mistakes as soon as possible in order to minimise delays.
- How will critical information be shared between the tab team, adjudication core, and logistics/convening teams? For smaller/medium sized tournaments a group chat augmented by phone calls (assuming everyone knows everyone else's number) can be sufficient, but even then, you need to ensure that any critical information conveyed privately (i.e. in a call or in person) is conveyed back to the group channel. At very large tournaments (or if you have the resources) walkie-talkies are an excellent way to manage communication — just make sure you have (ahead of time) reserve the different channels to a distinct and known purpose (i.e. general discussion; just the tab team & adjudication core; just convenors).
- As part of this it is ideal if the organising committees can procure local SIM cards for members of the tab team and adjudication core who are not local. These should be relatively generous in their plans — you don't want to worry about running out of minutes or data if on a critical call or using a hotspot to make critical allocation adjustments.
- At major tournaments you want to arrive at least a day before check-in; and ideally whenever it is that the adjudication core is arriving for their own preparation.

Registration
------------

Having effective registration systems and processes is one of the most important aspects of preparing to tab a large tournament. Bad registration data *will* make setting up a tab extremely painful and introduces the chance for mistakes or inconsistencies in tab data that will only come to light in the first round. As such:

.. rst-class:: spaced-list

- You should check in with the registration team and see what they plan to do as soon as possible after being brought on-board. As part of this you should make it clear that you should be consulted on any decisions they make about what data to collect, when to collect it, and how to collect it.
- Registration data should be collected into a shared and live-updating source, such as a Google Sheet. There should be as few canonical sources (ideally one) of data as possible; i.e. there should be a single sheet for individual details, a single sheet for team details, etc; and these should be maintained all the way through to check-in. For both you, and the registration team, having multiple conflicting or outdated copies of data will lead to errors. However, for the registration team these errors can usually be easily sorted out in person (at check-in) but for you that information always needs to be reliable and up to date otherwise what is imported into the tab cannot be trusted.

  - At this point our recommendation is to, in most cases, not use specialised registration systems as they are somewhat less intuitive and less flexible than setting up good Google Forms/Sheets.

  - If, for whatever reason, the registration team are not able to give you 'live' access to the data they have on hand, make sure they send you copies of it (even if it is incomplete) well before you need it to setup the tab itself. You want to be able to verify what data is actually being collected and how it is formatted well in advance.

- You should have access to *all* of the data collected; often registration teams will make (false) assumptions about what you do or do not need. It is better to have everything and then selectively filter out what is not relevant to the tab.
- It is critical that the registration team should check in with you before setting up forms asking for information. Every additional time that registration asks for data there will be less and less participation in the process, so you should aim to gather all that you need at the first opportunity; typically during the canonical individual registration phase. Particular information that should not be overlooked for tab purposes:

  - Individual registration should ask whether a participant is a speaker or an adjudicator.
  - If that person is a speaker it should ask for their team name/number (reconciling these later is painful).
  - Individual registration should ask for any accessibility requirements of both adjudicators and speakers.
  - Individual registration should ask for the previous institutions of both adjudicators and speakers.
  - Individual registration should ask for the email addresses of all participants.
  - Individual registration should ask for the phone numbers of adjudicators.
  - Individual registration should ask for the gender identity of both adjudicators and speakers. Even if you are not *planning* on using this to inform processes, such as adjudicator allocations, you want it on hand in case plans change.

- Independent adjudicators and the adjudication core should follow normal registration procedures. Having them not go through the normal process makes it easy to overlook their data or not get a complete picture of it. For example, adjudication core members might forget to nominate conflicts, or neglect to provide their previous institutions.
- You should confirm how the registration team plans to manage how people check-in to the accommodation in particular. Check-in is when issues with registration data come to light and it is vital that these changes are noted and recorded. Some form of validation of registration data *must* occur at check-in — in particular all adjudicators should be (individually) verified as present and all members of a team should confirm their presence along with their team's name/number and speakers.
- After check-in you need to have a definitive list of who is physically present at the tournament so you can run a first-round draw with confidence. Registration must know this and have processes in place for recording people individually as they arrive, and for that data to filter back to you.

.. note:: If you are using Tabbycat's secret links for feedback or ballots these are best distributed at check-in. The registration team should know about this, prepare for it, and be provided with the pdfs to print and distribute.

Adjudication cores
------------------

If there is a group chat for the adjudication core you probably want to be part of it; even if you don't contribute much. There are lots of small things that end up being discussed without consideration of how they will affect tab issues and it is also a chance to get to know — ahead of time — the people you will be working with closely over the tournament.

Members of the adjudication core will often leave tab-relevant decisions until the days prior to the first round or whenever it is that they can first meet with the tab team in person. This often wastes critical time and forces rushed decisions. Many considerations can instead be raised and discussed prior to the tournament. These could include:

.. rst-class:: spaced-list

- How to manage the feedback process. This typically benefits from foresight and pre-planning, rather than being decided on the ground. Key considerations are:

  .. rst-class:: spaced-list

  - Who submits feedback on whom? Do trainees do so on their chairs? Do panellists do so on each other? (Presuming your tab software supports these options).
  - Is feedback mandatory? If so, how will this be enforced exactly?
  - How much weight does each adjudicator's test or CV score have over the course of the tournament? By Round 3, or by Round 8, what proportion of an adjudicator's score is derived from their test and what proportion is derived from their feedback?
  - Will the adjudication core tweak an adjudicator's score to 'artificially' increase or decrease it to where they think it should be. For example, this could be done by adjusting a test/CV score upwards in order to compensate for bad feedback that (for whatever reason) they did not think was reliable or fair? Depending on your adjudication core's preferences and your tab software's allowances it is not unheard of for them to maintain full manual control over scores by reading/processing feedback results but only ever manually adjusting scores as a result (rather than having it automatically adjust due to the ratings in the feedback).
  - What is the score scale going to be? What do each of those numbers represent? How will this be communicated to participants so they can score accurately and consistently?
  - What kind of questions will feedback forms ask? If using :ref:`customisable printed or online forms <adjudicator-feedback>` consider how these questions be used tactically to identify key issues (say discriminatory scoring) or more easily identify people who should be promoted/demoted. While managing feedback is often a messy and subjective task, it can often be improved by being more targeted in what data it collects.
  - How will feedback be monitored, and how will this information feed back into the scores and allocations? At large tournaments it is not unusual for an adjudication core member to sit off each round to review and process feedback — there isn't really a good stretch of available time to do so otherwise. However even if doing this note that there are communication issues to manage here, as each adjudication core member will each end up with a relatively incomplete overview of the total volume of feedback.

- If possible it's nice to plan in advance for when the tab will be released (i.e. on the last night; the day after; etc.) as this often gets left to the last minute to be decided. Also the possibility of whether people can redact themselves from tabs should be raised, as that might be useful to inform participants of during online registration or tournament briefings. In a similar fashion, some adjudication cores might also want to limit speaker tabs to only a certain number of places, particularly at novice-centric tournaments.
- How to handle conflict collection; see the following section.
- How to handle the submission of scoresheets and feedback, primarily in terms of which parts of the process should be done online and offline. Some adjudication cores will have strong thoughts here; others will happily follow whatever you recommend. Key considerations:

  .. rst-class:: spaced-list

  - Paper-based feedback is much more taxing to enter than paper-based scoresheets —  typically there is much more of it; it asks for a greater variety of data; and it is submitted at inconsistent times. The one advantage is that it is easier to make feedback mandatory with paper, as you can ensure all teams and adjudicators have done so prior to leaving the room. Thus, in most cases, a good online feedback system is much more preferable than paper. If using paper be aware that you will need a lot of volunteers to ensure the feedback is collected promptly. If internet or smartphone access is limited at your tournament it is probably best to accommodate both paper-based and online methods.
  - The consequences of having incorrect or missing ballots are much more severe than for feedback. As such major tournaments use paper ballots in some form as the final stage in a checking process to ensure that the results of a debate are definitely correct — adjudicators will always make mistakes and while digital ballots can catch/prevent some types of error (i.e. a low point win) they can't catch others (assigning the wrong scores to the wrong speaker, nominating the wrong winning team, etc.). Assuming your software supports both options, the choice is thus whether to use a hybrid approach (online submission followed by paper verification) or to rely entirely on paper. A fully-paper based approach will be simpler for both yourself and adjudicators, and can be almost as efficient if you have a sufficient number of volunteers. In contrast, a hybrid approach will be potentially much faster if you are short of volunteers and if you expect that almost all adjudicators will have access to the internet, a smartphone, and are capable of following instructions.

.. note::  In some circuits, and when using some particular tab software, tournaments might run a 'dual tab' where there is a second, independent, version of the tab software and database into which all data is *also* entered. From what we understand this performs a dual role, as both a backup system that can take over from the main one (say if internet access drops) and as a way of verifying ballot data (by comparing draws or databases between software rather than having a two-step entry process operating for a single tab). This practice seems obsolete when working with modern web-based tab software that is capable of backing up and restoring to an offline system, but we would like to hear your feedback if you think that is not the case.

Conflicts/Clashes (registration/equity/adjudication core)
---------------------------------------------------------

.. rst-class:: spaced-list

- There should always be a *single* means of collecting conflicts (i.e. a single Google Sheet/Form) and all conflicts should go through it. Because the nature of this data is sensitive and evolving, there must be a single location where it can be easily captured and verified as having been entered into the tab. Conflicts data should never be spread across a loose collection of emails/personal messages/spreadsheets; otherwise keeping track and knowing which ones have been entered into the system will be painful and error prone. Get in touch in with equity and registration in advance and make it clear that they should not make their own conflicts form; or if they've already made one, make sure you adopt it and have access/control of it.
- Conflicts should, ideally, *only be collected after a participants list has been published* and requests for people to nominate conflicts should also be sent out as few times as possible. Most people will only fill this form in once, so it is vital that when asked to nominate conflicts they have as much information as they need to do so comprehensively. Without a public and reasonably-complete participants list people will either nominate conflicts that are not present (wasting your time in cross-referencing data) or not realise someone is present and raise the conflict at a latter, less opportune time.
- In some circuits only adjudicators are allowed to nominate conflicts because of the risk of teams using conflicts 'tactically' to block adjudicators that they think are terrible judges. However, having teams nominate conflicts can be useful: adjudicators may overlook a conflict or there may be equity-based reasons that a conflict is non-symmetrical. This trade-off can be handled in two ways:

  .. rst-class:: spaced-list

  - Not allow teams to nominate conflicts during registration; but allow them to approach equity teams before, or during, the tournament to identify the conflict. Equity can then raise the issue with the tab team and adjudication core and it can be added to the tab.
  - Allow teams to nominate conflicts during registration; but have the adjudication core review the data for 'tactical' conflicts. These are usually relatively easily identified, although can be overlooked if the adjudication core does not know the participants or their region/circuit well. The adjudication core can then override the conflict, discuss it with the teams, or raise it with equity. However, if going down this route, the tab team should discuss with the adjudication core how to manage this process well-ahead of the tournament, and ensure they actually do review the conflicts prior to the first round — otherwise it will likely surface during an allocation and become a major distraction during a critical time period.

- As mentioned in the previous section, the adjudication core (possibly with equity) should provide some degree of guidance about what kinds of debating-related conflicts should be provided. People should be able to self-define what constitutes a conflict, but there are circumstances where they are overly cautious and can be reassured that it is not necessary. The opposite problem may occur also, where many people may have a very high bar for what defines a conflict which could lead to perceptions of bias from other participants.
- Generally, it is preferable that each form nominates a single conflict, and people are asked to re-submit for each conflict they are adding.

  - To save you some hassle the conflict form should make this very clear (i.e. that one conflict = one submission; ensure the field labels reinforce this)
  - The conflict form should also make clear that you shouldn't use the form if you don't have any conflicts (i.e. people will submit 'None', 'None' etc)
  - The conflicts form should also make clear that adjudicator's don't need to submit a conflict for their current institution and that team's don't need to submit conflicts for adjudicators from their current institution.

- In poorly-structured conflict forms, identifying exactly who is doing the conflicting and who is being conflicted is a nightmare. You want to structure the questions to minimise this ambiguity. A form should definitely ask:

  - Who are you (the conflict-specifier)?
  - Are you a team or an adjudicator?
  - Which institution are you from?
  - If part of a team, which team are you in?
  - Who are you conflicting?
  - Are they a team or an adjudicator?
  - Which institution are they from?
  - If they are in a team, which team is it?
  - Have previously attended any other institutions; or have other reasons to conflict entire institutions? If so, specify those institutions.

- Note that this last question can be tricky to deal with; good tab software will let you conflict an adjudicator from an institution other than their own, but it is harder to mark an individual team as having members previously attending another institution. These circumstances are rare and typically very 'soft' conflicts but are probably best handled by creating individual conflicts between that team and adjudicators from the previous institution in question.
- Adjudication core members will often not nominate their own conflicts; presuming that they will notice and correct them during allocations. They often forget or overlook this. Their conflicts should be entered as per normal.

Scheduling (convenors / venue organisers)
-----------------------------------------

One of the easiest ways to have things run late is to set an unrealistic schedule. As much as possible the timing allocated to rounds (inclusive of events such as lunch or committee forums) should conform to an even distribution of how long it takes to process results and create a draw/allocation — you don't want to be in a position where particular rounds have too much time and others too little time to spend on allocations and other crucial tasks. This is something that should definitely be working on in conjunction with convenors and other critical parties before they lock down timing details with food suppliers or the operators of the debating venues.

Note also that in most circumstances it is preferable to create a draw and allocation for the first day of the next round at the night before. This time should be built in to the schedule of the previous day, and raised with the adjudication core so they don't expect to be able to immediately depart after the day's rounds are done.

Below is the time taken within each round at Australs 2017. For context, this was neither a particular efficiently or inefficiently tabbed tournament. Notable details:

.. rst-class:: spaced-list

- The tournament was ~40 rooms each round and had access to 3-6 runners and data enterers. Paper ballots were pre-printed and distributed by runners to rooms prior to the debates starting, then collected sometime after the 15 minute deliberation period. Feedback was submitted online. At Australs all adjudicators (excluding trainees) submit their own ballots.
- The adjudication core were neither particular slow nor fast in allocating adjudicators compared to other adjudication cores. At Australs most adjudication cores will create allocations by using first running an automatic allocation then extensively tweak the results.
- There were no serious issues that delayed the tabbing of any particular round beyond the routine and expected issues of last-minute draw changes, adjudicators producing incomprehensible ballots, etc.
- Whilst the tab ran relatively quickly, there were minor delays because of mismatches between the planned schedule and the optimal schedule from a tab perspective.
- A round at Australs takes around 2 hours from a debater's perspective: 30m of prep, ~60m for a debate, ~15m for deliberation, and ~15m for the oral adjudication and feedback.
- We didn't note the timing of data-entry in Round 8 as there was no time pressure. After data entry was finished, finalising and double-checking the breaks took through to ~7-8pm.

======================  ===============  ===============  ===============  ===============  ===============  ===============  ================  ===============
Day                     One                                                Two                                                Three
----------------------  -------------------------------------------------  -------------------------------------------------  ---------------------------------
Round                   1                2                3                4                5                6                7                 8
======================  ===============  ===============  ===============  ===============  ===============  ===============  ================  ===============
Draw generated          *Night prior**   12:43            16:12            19:17*           12:05            15:46            19:10*            12:07
Allocation finished     *Night prior**   13:17 ``+34m``   16:36 ``+24m``   20:28* ``+71m``  12:58 ``+53m``   16:24 ``+38m``   21:30* ``+140m``  13:25 ``+78m``
Motions released        09:28            13:50 ``+33m``   16:47 ``+11m``   09:22            13:14 ``+16m``   16:40 ``+16m``   9:30              14:18 ``+53m``
First ballot received   11:51 ``+143m``  15:46 ``+116m``  18:52 ``+125m``  11:18 ``+116m``  15:13 ``+119m``  18:40 ``+120m``  11:35 ``+125m``   ?
Last ballot confirmed   12:38 ``+47m``   16:07 ``+21m``   19:15 ``+23m``   12:05 ``+47m``   15:44 ``+31m``   19:09 ``+29m``   12:06 ``+31m``    ?
======================  ===============  ===============  ===============  ===============  ===============  ===============  ================  ===============

Tab Setup
=========

Setting up a tab site is the most technically challenging (or at least annoying) part of tabbing. It is where you need to reconcile large amounts of data and configure a variety of settings to ensure everything will run without issues during rounds. While this is often done a day or two before the tournament, ideally you should look to do as much as possible in the week or two beforehand where there is much less time pressure.

Importing data: workflow
------------------------

.. rst-class:: spaced-list

- First check with registration people if their data is complete, and if not who is missing. If it's only a few people it's viable (for tab purposes) to use place-holders for them, as long as you remember to follow up and edit their data manually later.
- Familiarise yourself with the different methods for importing data into your tabbing program. Typically, these include options for bulk-importing spreadsheets, for adding information piece-by-piece through a graphical interface, or a hybrid systems. Depending on your tabbing software it may be easiest to first setup your tournament on a local copy of the tab (where it will be faster to rectify mistakes) and transfer the data to the live site when everything is mostly complete.

.. note:: If you are using Tabbycat our spreadsheet importer is definitely easiest to use on a local copy; however using the visual importer is perfectly viable for larger tournaments if you are not comfortable with the command line. When using the spreadsheet importer note that it will likely take several iterations to get the data to import cleanly as there will typically be small mismatches in speaker/institution names and the like.

- If the tournament (or the host society) has their own domain name and your tab software is self-hosted consider whether you want to setup the tab site on their domain so that the URL is nicer and/or easier to type.

.. note:: If you are using Tabbycat, and deploying to Heroku, be sure to read our documentation about the size of Postgres database your tournament will require. Setting up the correct size of database from the start is the best way to go, as transferring information at a later stage is a hassle and could delay the tab at inopportune times.

Importing data: regions/societies
---------------------------------

.. rst-class:: spaced-list

- Societies will often have special names that they like to use in draws (that are not the same as their institution's name or acronym). These can be gathered from institutional reps or from prior tabs. When in doubt err on the colloquial / most recognisable name; particularly for formats where teams need to find each other prior to the debate.
- If your tabbing software has methods for assigning region information to teams and adjudicators (for diversity purposes) determine with the adjudication core the types of regions that will be used.

Importing data: participants
----------------------------

.. rst-class:: spaced-list

- Check you have emails/phone numbers included in your data that will be imported (presuming your tabbing software supports this) there are useful to have on hand later for either emailing out information or quickly following up errant adjudicators.
- Often, the easiest way to prepare registration data for tab imports is to create new tabs in the registration spreadsheet, and use referencing to automatically order and arrange their data into the format your tab software wants. If the registration data changes significantly this will also make it easier to re-import things.
- Often some adjudicators, typically local independents, may not be available for all rounds. Try and find out who this affects and when; once data has been imported you can :ref:`pre-check these adjudicators in and out of rounds <availability>` (if your tab software supports this; otherwise note it for later).
- Remember that the swing team(s) probably also need to be imported into the tab.

Data import: rooms
------------------

.. rst-class:: spaced-list

- Ideally you want not just a list of rooms, but also of their types and categories — i.e. what building a room is in and/or it will be coded so that participants can find it.
- You want to know if access to some rooms is conditional; i.e. if some rooms are only available for some rounds. Again, if your tab software supports it you can :ref:`record this availability information into the system <availability>` (once data is imported) otherwise you can note it for later.
- Registration should have collected information about accessibility requirements; they should be imported into your tab software (if it :ref:`supports automatically matching accessibility requirements <venue-constraints>`) or note for later. In general you will also want to use a similar process to ensure that members of the adjudication core are assigned rooms that are close to the tab room.
- You also want some idea of priority; that is to say if some rooms are inconvenient (and you have more rooms than you need) they should be marked as a low priority so they will be allocated only if needed. Again, this might be automatically done by your tab software or something you will need to note and manually change after each draw is made.

Data import: adjudicator test/CV scores
---------------------------------------

- Ideally the adjudication core should do this themselves as they are marking the test or scoring CVs. If they won't, or you don't trust them with full tab access, be prepared to do so yourself.

Data import: tab access
-----------------------

- Set up user accounts for the adjudication core with dummy passwords (they can change them later).
- Set up user accounts for runners/assistants with dummy passwords (they can change them later).

.. note:: If using Tabbycat and using online ballots or feedback with the private URLs method, participants should be emailed out their private URLs before they start travelling to arrive at the tournament (i.e. when they have a reasonable chance of checking their email). This can be done using the inbuilt pages on Tabbycat, or by importing participants data into a service such as Mailchimp.

Pre-Rounds Setup
================

Setting up the tab room
-----------------------

This is typically the first order of business, as all future pre-round setup tasks (i.e. training the adjudication core, testing printing, etc.) are better for being done in the same space that will be used throughout the rounds. Once you're in the space there are a couple of small checks to run through before the larger question of how to arrange and use the space should be tackled:

.. rst-class:: spaced-list

- Check with convenors whether things can be left in the tab room overnight. If they can't you'll need to make plans for how to move any big items (printers; ballot stacks) to and from the tab room each day.
- Check that the internet access in the tab room is reliable.
- Check that the projector system works, both with whatever wired-in computer is in the room and when connected to your laptop.
- Check what items either yourself, or the organisers, have at hand and check if anything needs to be acquired before the next day. Critical items for tab rooms are typically:

  .. rst-class:: spaced-list

  - An extension cord with multi box; ideally a pair of each.
  - Whiteboard markers (assuming there is a whiteboard) otherwise permanent markers and large sheets of paper (i.e. A2) can suffice.
  - Boxes. Lots of boxes. Loose ballots are a source of confusion and error, so you want some way of temporarily storing ballots as they proceed through the entering and checking process. You probably want at least three large boxes (for ballots to-enter, ballots to-check, and finished ballots) but more will be useful.
  - Spare printing ink/toner, and paper for the printer. Ideally your paper would be multi-coloured, with each colour being used for a different round. Pastel colours are ideal, and you ideally want at least three different colours so that you don't have to repeat a colour within the same day. Be sure to calculate how many sheets you will need per round and ensure you have a generous number of spares.
  - If tabbing a format that can produce multiple ballots per-debate, staplers are essential to keep those ballots organised. Buy at least two sturdy ones.

- Non-essential, but often useful to have items:

  .. rst-class:: spaced-list

  - Whatever dongles/adapters you need to connect your laptop to the projectors, both in the tab room and in the briefing room.
  - An Ethernet cable (or two) as a backup option if WiFi drops or is overloaded.
  - Post-it notes are a great way to temporarily mark ballots with information; typically used to indicate ballots that need correcting.
  - You'll often need to make impromptu signs; sticky tape and/or blu-tack are good here
  - Spare pens for the people doing data entry to use
  - Trash bags for collecting rubbish as it accumulates
  - A Chrome Cast can occasionally be very useful if a projector or screen doesn't have accessible input cables or so that you can use a projector without having your laptop tethered to a particular podium and desk.

If you haven't already it's a good idea to check your printing setup by printing off a bunch of generic ballots and feedback forms to have on hand if the need arises (i.e. a ballot is missing and needs to go out ASAP; or if someone can't do feedback online and needs to do so on paper). At worst, the blank ballots you print can be used for the out-rounds. While printing these off, time how long it takes the printer to print say 25 ballots and extrapolate from that to figure out how long it will take to print the entire round's worth of ballots. Note that if printing off a round's ballots is relatively quick it can be useful to delay it in order to better accommodate any last-minute changes to the draw that happen post-announcement. It's also worth thinking about how you (or at least who will) group up the printed ballots in order to distribute them to runners.

At this point you should also setup whatever process you need for managing runners and the ballot collection process. At a minimum, this should probably be a spreadsheet or a list on a whiteboard outlining the different groups of rooms with spaces to mark in which runners are delivering/collecting ballots for each location. Who is running where might change from day to day and should be kept updated. It should also have some method for contacting each runner (i.e. a cell phone number).

The question of how to arrange the actual room is one with many answers, and is obviously shaped by the peculiarities of the space itself. However there needs to be some system behind it so that people know exactly where to go and what to do when there is time pressure.

The key consideration behind this system is typically the 'flow' of ballots: what happens after they are brought back from runners, but before they are completely entered into the system. Think through how you want this process to operate and how the space can be arranged to make each step as smooth as possible. Considerations:

.. rst-class:: spaced-list

- When runners initially return a big stack of ballots, what happens? They could be transferred directly to the data-enterers to start on, but it is often useful to have preliminary checks here in order to keep the job of the data-enterers as simple as possible. These checks could include:

  .. rst-class:: spaced-list

  - For formats with multiple ballots per-debate, you typically want to identify and staple together all the ballots from a given panel.
  - For tournaments where ballots are liable to go missing (or for when you have plenty of data-enterers and want peace of mind) it is worth using the :ref:`ballot 'check-in' system of your tab software <data-entry>` (if it has one) to mark off ballots as physically present in the tab room. This allows you to quickly identify which ballots are missing and begin tracking them down earlier than you would do otherwise if just waiting for the 'to enter' pile to be exhausted.
  - Depending on your preferences and resources, ballots could at this stage be checked for errors. This could include a basic sweep for missing information (i.e. totals) or a comprehensive sweep that includes checking math errors, ambiguous handwriting, low-point wins, etc.). While this will delay the time between ballots arriving and being entered, it will mean that you can start correcting ballots sooner, and lessens the burden on (potentially inexperienced) data-enterers to check and catch these. If you have many runners, and they are familiar with how debating scoring works, this is recommended.

- Once this preliminary step has occurred the next task is actually entering the ballots. The number of steps here is dependent on your tab software and tab settings; you might have had the 'draft' ballot be submitted online by chairs or you might have the whole two-step process of a 'draft' ballot entry and the 'confirmed' ballot entry taking place within the tab room. Considerations:

  .. rst-class:: spaced-list

  - Regardless of whether you are working with a one-step or a two-step process, you want to arrange the tables where data-enterers are sitting such that their need to move is minimised. That might mean either have a central inbox of ballots to enter in the centre of the tables (such that everyone can reach it) or having multiple 'clusters' of enterers around boxes.
  - If work with a two-step process you want those two steps to be an active part of the spatial arrangement. That is to say, typically there will be a grouping of enterers who are working on the initial ballot entry (clustered around a box or boxes) and then a separate 'downstream' grouping of enterers that work on confirming/validating those entries. Depending on the size of tournament and quantity of runners, you either want it so that individuals from the first group can easily pass their ballots to the box of the second group; i.e. by reaching across the table or walking a short distance. At huge tournaments, you might want a dedicated person to transfer ballots between boxes to prevent enterers having to get up.
  - In a two-step process people may need to transfer roles, as generally you want to prioritise entry and then validation. Often this isn't necessarily much more efficient, but if 'rebalancing' the roles make sure that the spaces assigned to each role can accommodate extra people, and that people physically move to occupy each role.
  - In general, you want to minimise the number of ballots that each enterer feels the need to 'hoard' to work through to keep the work evenly distributed. If people are taking a large number of ballots to process, at the final stages of entering some people will have a bunch to work through while others will be finished. Making it easy to collect and pass on ballots in the space itself helps cut down on this while keeping entry efficient.
  - While the exact spatial arrangement depends on your numbers and what furniture is available, a long rectangle is a good starting point as the ballot process is in general linear (check, enter, validate, finish). Typically, this might look like a series of tables in a row with enterers sitting on either side and with the various ballot boxes in the middle.
  - When ballots have finished being enter/validated there definitely should be some sort of final 'done' box. Take care how ballots are put here, a common source of error is people putting ballots there before they are fully finished.
  - When ballots need to be corrected you generally want to 'extract' them from this process and hand them off to a tab-director or assistant to chase up and collect. There should be a forethought process for managing this; and ideally a dedicated space for it to prevent ballots being lost and to make it easy to identify ongoing issues. This might look like a process of sticking a post-it note (outlining the error) to the ballot, and then pulling it from entry/validation and placing it on a desk. Ideally you also want one of the tab directors always *not* doing data entry so that they are immediately available to manage this process.

Training volunteers
-------------------

If at all feasible you want to train that volunteers acting as runners and/or data enterers the day *before* the tournament starts otherwise the first round will be rough. It's generally a good idea for this training session to generally mirror the process of running a round. It's also generally a good idea that — even if you have enough people for dedicated runner and data-enterer roles — to train all volunteers so that they are familiar with each role and can fill in if needed. This has a couple of stages:

.. rst-class:: spaced-list

1. Introductions and details

  .. rst-class:: spaced-list

  - Volunteering is typically thankless and often stressful. It's also quite a dull and mechanical process: deliver paper; collect paper; enter numbers; check numbers. Given the rather unglamorous nature of their role you want your volunteers to feel welcome and a crucial part of a wider team. When meeting everyone for the first time try and run the introductions in a non-perfunctory manner and get to know people's background/interests and outline how valuable they are to the tournament.
  - As part of this process you should, note their cell phone numbers or whatever means you will use to coordinate communication between the team.
  - Figure out what will be happening during downtime and how you can make it more enjoyable. Would volunteers like to watch debates, work in the tab room, etc. Is there anything they would like during those down times (music, snacks, coffee, etc.).

2. Rooms and Running

  .. rst-class:: spaced-list

  - If runners are unfamiliar with debating in general, outline the basics of what draws are, what ballots are actually for, and what this process looks like from a debater's perspective.
  - Outline how/when the printing process occurs and who will sort/assign the ballots. Now is a good time to assign different runners to the different groups/rooms that they will be working with.
  - It is critical that, as a group, you actually go to everyone one of the venue groups and identify all of the venue rooms that are listed so that everyone knows exactly where to go. This may take some time. But it is a good chance to both check those rooms actually exist and pre-identify any problems that might occur with runners and debaters finding them.
  - Outline in general what happens during ballot collecting: when to do it, how to approach chairs, what do to if they are slow or delaying. You should raise the chance of chairs being belligerent and outline how they (and you) should deal with this.
  - If you are having runners pre-check ballots it's a good idea to fill out a few 'bad' ballots to demonstrate the kinds of checking required. If you are using any communication systems (i.e. having runners mark of buildings as 'done' in an online system) go through that now also.

3. Data entry and checking

  .. rst-class:: spaced-list

  - Before starting, setup logins for everyone and show them how to login. Also get an idea of what devices they will be using, or can bring, for data entry purposes. Check/ensure that they will have internet access on those devices.
  - Run through this in the actual tab room; illustrating examples with actual ballots and going through the roles in the actual spots which they will occur.
  - Run through how the seating/table/box arrangement works and the types of roles at different positions.
  - Emphasise that in general, any ambiguities should be raised with the tab directors/assistants; i.e. that you should never guess about ballots but instead always delegate resolving issues to someone else.
  - Run through the different edge cases and things to check during entry. For example Iron Person speeches, mismatched totals, entering the wrong ballot for the wrong panellist, etc (see section below). Be sure to also go through what happens when the validation step fails; i.e. when a ballot needs to be re-entered.

Training the adjudication core
------------------------------

Typically making the first-round's draw and allocation is the best time to really run through how your tab software and processes work in a 'real' environment as well as the expectations surrounding their and your role. Generous amounts of time should be budgeted for this; it's not uncommon for it to take up most of an evening. It's also worth having an older tab, or a tab full of fake data handy in order to show them how, say, the feedback or allocation interfaces look like when full of data.

To kick off you should probably setup tab logins for the adjudication core as necessary, outline what kinds of access they have, and (particularly if they haven't used your tab software before) outline broadly what pages they should and shouldn't access. In particular, show them how to find and parse feedback as that is often the interface where they will be spending most of their time individually. As part of this tour outline (if you haven't already) how feedback will work, as well as the means by which the adjudication core can use the tab software to keep track of feedback as it comes in. Ideally some sort of general strategy should be formed for this, so that particular people sit out rounds, or are delegated the task of catching up on feedback at other points.

Depending on how many runners you have it may be necessary, or beneficial, if the adjudication core helps out with data entry. However, if you go down this route the adjudication core need to be highly trained; they are often much more likely than volunteers (who are less self-confident and have more experience) to make errors. Whether you do or don't do this, ensure that adjudication core members know to come to the tab room ASAP after they have finished adjudications rather than swanning around socialising or going to lunch. Draws will often be held up just by the fact that not enough adjudication core members are present to start or finish an allocation.

The first-round allocation is the last thing you want to cover. It is typically your only change to slowly and comprehensively walk the adjudication core through the allocation interface and the allocation system.

Allocation interfaces, while often complex, should be stepped through so that the adjudication core knows precisely how to operate it themselves (if needed). They should know what it can (and can't do) and how the different features can be used and activated. For example, diversity highlights might be an optional toggle (in which case you explain how to active it, when to do so, and what it represents) or there might be parts of the interface that detail information such as a room's liveness, energy, or bracket which should be highlighted and explained (i.e. how 'liveness' is determined).

Secondly, and most importantly, is outlining how the automated process of adjudicator allocation operates, and how this can be made to match the adjudication core's preferences. Typically, you want to rely on automatic adjudicator allocations as much as possible in order to decrease the time taken to do an allocation; however every adjudication core has a different philosophy on what their perfect allocation looks like, and it is your job to try and align that ideal with what the automated system produces as much as is possible. The precursor to this is yourself knowing how your tab system allocation works: what is the relationship between a debate's bracket (or assigned priority/energy) and the numeric ranking of the automatically generated panel? Does the software optimise panel strength for a voting majority, or across all panellists? When does the software allocate solo chairs over panels? How does it avoid conflicts? Does it have (and enforce) particular expectations for a given adjudicator's score; or does it rely on a more relative comparison? The answers to the questions will often be dramatically different between different programs and you should know them in advance.

Most tab software will have at least some options for you to configure those automated processes — either by changing the automatic allocation's parameters directly or by controlling the ranking and feedback systems that feed into it. The first round is the prime opportunity to configure these options so that they align as close as possible with what the priorities of the adjudication core. If your feedback ranking system is mismatched with how you expect the automatic allocation to place adjudicators, or if the distribution of adjudicators across the draw is not what you expect, the adjudication core will end up wasting significant amounts of time adjusting allocations. Even if things work well using the default settings, ensure you experiment and demonstrate the consequences of changing the settings just to show that it can be done, what the general effects are, and to see if there are even-better configurations.

.. note:: This process of tweaking the automatic allocation settings is one you should also revisit as the rounds progress.

How to approach diversity (typically in terms of region and gender) across an allocation in particular is something that some members of an adjudication core will not have had to consider in the context of a large tournament with time pressure or in terms of having to make explicit trade-offs. Again, you should make it clear how the software can accommodate this, and get the adjudication core to plan for how (in general) they want to approach this. Often it will form the final phase of the allocation process, and so can easily be forgotten or skipped over; or people will have different philosophies of how to approach this which are only raised at critical points.

Outline that there will usually be a trade-off between the quality of each allocations and the speed at which the tournament runs. When time is not a factor, many adjudication cores will often take an hour or more in order to create a perfect allocation; but they should know though that aiming for perfect during many rounds will break the schedule. You should try and get them to set some sort of time goal for allocations, and (during the rounds) ensure that they are aware of when they are going too fast or too slow. Depending on your personal preferences and the norms surrounding tab direction in your circuit you may want to actual enforce these time limits.

Finally, outline how you will all communicate. Again, there should be a single medium for this so that everyone knows what is going on; and this is ideally something that has been planned out beforehand with them and the organising committee. But at this point the tab team may have expanded, or there may be better options than what was being used previously. It's also worth outlining which parts of the tab team will generally be doing what roles and where — i.e. who will be rolling the draw, who will be chasing up people, etc.

Preparing a briefing
--------------------

.. rst-class:: spaced-list

- At large tournaments there should be some form of briefing covering ballots and feedback process, even if it is just quick one. Usually you will want to be the person to design and deliver this; other people less-familiar with the system may miss details.
- Liaise with convenors and the other people doing briefings to ensure (a) they know you're doing one; and (b) you are not overlapping in terms of content.
- See the last section of this document for notes on what can be useful to include here

Final checks
------------

.. rst-class:: spaced-list

- Check if the convenors have made a map that clearly outlines where the rooms are. Ensure it's clear and post it to either the tab site (ideally) or somewhere like Facebook.
- Check that convenors have some sort of way-finding system in place, i.e. chalked directions or colour-coded signs. Check these colour codes match the names of your venues.
- Check that the draw types are correct for each round in the tab system.
- Check with adjudication core if/when there are secret rounds and that these are correct in the edit data base area.
- Check how the draw will be displayed and managed. Is the projector good; how big does the text size need to be? How fast is the scroll?
- If you will pre-print ballots check that you've set the "return ballots to" configuration setting; even if it just says "to runners".

Managing Rounds
===============

Once everything has been setup and everyone knows what they should do, the actual process of running each round should go smoothly. It probably won't though. The earlier sections should have laid out what the ideal process for managing data entry and allocations, so this section will instead focus on what can go wrong and what to keep an eye out for.

Disaster scenarios
------------------

There are two broad classes of disaster scenario here. The first, and more rare case is when either internet access at the venue goes out or if a web service that your tab software depends on has an outage (for example, both Tabbie 2 and Heroku-deployed Tabbycat instances depend on Amazon Web Services). The first can at least be solved temporarily if tethering is available, but if that is not possible (or the latter case occurs) you may need to switch to using an offline copy of that tab by restoring from a backup if the outage is non-transient.

Obviously, for this to work, you should be taking regular backups using whatever mechanism your tab software allows. Key times to do so are critical events such as finishing entering a round's data or finalising an adjudication allocation as these are especially difficult to recreate. Importantly, these backups are only useful to you if you have a downloaded copy of them; ideally download to a Dropbox or some other cloud service that will spread them across multiple computers and an online service.

Having an outage of internet access or a key web service go down to the point of having to switch to an offline tab is an exceedingly rare event, but one worth planning for at large tournaments. That is to say you should have ideally have an offline copy of your tabbing software setup on your local machine, and know how to restore a backup to it if necessary.

Backups are also useful as guards against a much more common source of error: data loss caused by user error. It is not unheard of for even experienced tab directors (or inexperienced adjudication core members) to accidentally delete an entire allocation, delete a round, or some other form of destructive action that would require a lot of work to redo. Taking backups at key points, and knowing how to restore them (to the online copy of the tab) is a useful — and occasionally essential — skill.

.. note:: The much more common source of a major tab disruption is a major user-error or a bug within your tab software itself. Fixing these will be highly-context dependent and the best way you can prepare for them is to know your tab software well enough to understand what might have caused it or be able to contact someone else who does. That said, having backups on hand can also allow you to restore your database to before the bug or user-error occurred and try to proceed without re-triggering it.

Expected problems
-----------------

Incorrect ballots are an inevitable tragedy. Many more optimistic tab directors will imagine that these can be prevented through sufficiently detailed briefings, recurring public shamings, or fool-proof ballot designs. While these might help in cutting down the number of errors, eliminating them entirely seems to be an unachievable goal. Note that this is particularly true at international tournaments and/or at tournaments that draw participants from circuits which have more than one predominant format.

While debaters as a whole display astonishing levels of innovation in discovering new ways to incorrectly fill in a ballot, there are a couple of broad cases that you should look out for an prepare people to deal with:

.. rst-class:: spaced-list

1. Not adding up score correctly. Pretty much everyone who does this will note that this is the first time that it has ever happened to them.
2. Omitting some information. Most common are not filling in total scores, the nominating winner, or the margin. Having omitted an entire team's scores or speaker names is not uncommon.
3. Scores that are outside the range.
4. Low-point wins, or tied-point wins. Typically occurs in conjunction with (1).
5. Poor handwriting rendering numbers illegible. While one could 'guess' whether a number is in fact a 6 or a 5 based on a team's total score, doing so is dangerous as it assumes that the person hasn't also done (1).
6. 'Correcting' information in an ambiguous way. For example, using arrows to swap a speaker's order (which is typically circular/ambiguous) or drawing numbers over other numbers in a way that makes it unclear which is the original and which is the replacement.
7. Ballots just going entirely missing because either a runner missed the room, the chair forgot to return it, or the chair just left it in the room.

Ballots aside, there are a number of other common occurrences that will necessitate changes to the drawn and allocations:

.. rst-class:: spaced-list

1. Teams will not turn up to debates, or turn up to debates extremely late. In both cases they will often not notifying anyone. Aside from needing to swap in a swing team in their place in the draw, it's worth keeping in mind that the necessity of a swing team might not be known until right when debates are about to start (which can lead to issues if you assume trainees or runners will be filling up the 'spare' swing team).
2. Adjudicators will also go missing. As with teams this can usually be caught during roll call; but might also not be known up until debates start. If the adjudication core is available they can make adjustments, but often you will need to make a call as to whether to form an even-sized panel or to redistribute adjudicators from elsewhere.
3. When a draw is released there will often be conflicts that were unknown to the tab system, and will necessitate making changes to the draw post-release. It's important that when making these changes you keep a clear record of what needs to change (if there are multiple swaps needed it can get tricky to keep track of) and ensure that all parties involved know about where they are being swapped to.

Ongoing checks
--------------

You will have a decent amount of downtime during rounds when debates are happening. A couple of things its worth keeping an eye on during that time:

.. rst-class:: spaced-list

- Ensuring your backups have been taken and downloaded.
- Ensuring the tab room isn't devolving into mess.
- If you can be bothered (and if no adjudication core member is doing so) reviewing feedback for critical issues (i.e. comments highlighting severe issues, or chairs getting very low scores) is a good way to be useful. If using paper-based feedback this can look like physically separating out these feedback forms for the attention of the adjudication core; while if using online feedback systems you may want to keep a collection of browser tabs to show.
- Chasing up the language committee (if one exists for this tournament) to confirm which teams are in which category and what their break preferences are (if multiple breaks are not allowed). You want to have this information confirmed as soon as possible as it becomes of critical value to allocations once the draw starts segmenting into live/dead rooms.
- Reviewing how efficiently things are running and whether there are any bottlenecks that can be better addressed in the next round. It's generally a good idea to (on a whiteboard or a spreadsheet) keep track of how long each stage of a round is taking (running, data-entry, allocation) and what (if anything) is causing delays.

.. note:: If hosting Tabbycat on Heroku keep an eye on the metrics section of the dashboard area, noting if there are 'timeout errors' and what the average response times are. Adding more dynos should help with both.

Breaks and Break Rounds
=======================

Generating the adjudicator's break
----------------------------------

Determining the adjudicator break generally involves a complex set of considerations rather than strictly ranking based on feedback. As such most adjudication cores will use whiteboards or Google docs to draft and discuss the possible options. One thing to note here is that breaking adjudicators will need to be marked as such in the tab at some point (both so they can be on future draws, and for publication) so you want to be careful that the tab is the final source of authority here — it is easy for information to get out of sync between what the adjudication core is using to draft the break and the system.

When the adjudication core is determining the break ensure that they have an idea of the *quantity* of adjudicators needed (breaking too few or too many will cause issues) and whether there are any special considerations (such as having conflicts with large portions of the draw, or leaving at a given point) that involve a specific adjudicator being considered.

Generating the team break
-------------------------

Before doing so in an automated fashion, first check in your tab software whether all teams are assigned to the right break categories. Depending on whether your software supports multiple formats you probably also want to check that each break category is using the right 'rule' specified by the tournament (i.e. a WUDC- or Australs- compliant break ranking). Also double check the break size itself is correct in the software.

Hopefully the automated system will generate a correct break, but this should always be checked against what you'd expect the results to be from standings. Note also that there are cases, such as when a team has to leave, or when teams are or are not double-breaking, that mean the automated break results need to be overridden (typically in Tabbycat you would add a marker or note to include their ranking, but exclude them from having a break rank).

Announcing the break
--------------------

Mistakes are made surprisingly often during results announcements. Again, this is often a problem with incomplete or out of sync data, where print-outs, slides, or the tab site itself might not reflect (for example) last minute changes about breaks or have potentially mixed up teams or adjudicators with similar names. Things that can help:

.. rst-class:: spaced-list

- Have a single source for what is being read out — i.e. a printed list (recommended) or the tab site itself — but don't mix and match. If making slides (often a good idea for large/crowded venues) copy the data from the canonical source being announced.
- Double check what is being read out against the tab site, and/or whatever draft lists were used to determine the adjudicator's break. Verify with the adjudication core that everyone who should be there is, and that nobody is missing.
- Clarify what information should be on the print-outs and the general order in which things are read. For example, it might be easy to omit breaking adjudicator's institutions, to use ambiguous abbreviations over full institution names, or to have an inconsistent approach to how the information is read (i.e. whether it is read as *wins* then *team points* then *team name*).
- Without revealing any details try and get at least some guidance on how to pronounce names that people are not familiar with pronounce.
- Have backup copies of whatever is being read from and clarify who is reading off what portions.
- Try to publish the break list on the tab website (or via some other online method) shortly after it is announced in order to minimise the chance of misinformation spreading.

Managing the out-rounds
-----------------------

Out-rounds are generally under less time pressure and can be managed by just one or two members of the tab team. However, they tend to be run in a more haphazard fashion, so there are a couple of things to keep on top of:

.. rst-class:: spaced-list

- You should keep track of which adjudicators have or have not been used throughout the finals allocations. It is easy for adjudication cores to forget to allocate someone and have to either drop them or promote them beyond what they had originally intended.
- It is very easy for ballots to get lost in break rounds as chairs have less defined roles and processes in what they do with their ballots. While having correct speaker scores correctly entered for break rounds isn't a strict necessity, it is nice to have and the alternative (using fake speaks just to record the winner) can cause confusion.  Closely manage distributing ballots to the chairs and collecting them as soon as possible afterwards; especially if there is any time pressure. Generally it is not worth printing off per-debate ballots; just print a stack of generic ballots at the start of the out-rounds and distribute as needed.
- You should know, in addition to when the break rounds are, when the results announcements are. Often these announcements are saved (for suspense or logistics reasons) until particular points of time (i.e. until the evening social; or until other out-rounds are finished). Obviously it's important not to accidentally release results; but often convenors and the adjudication core will often have different ideas about when results are meant to be released.

.. note:: If using Tabbycat to manage out-rounds with multiple break categories, note that the round progression is no longer strictly linear. So be careful with when/if results are released online and note that often you can't rely on online interface to release draws publicly.

Preparing for tab release
--------------------------

At some point, if you haven't already, have a discussion with the adjudication core about when the tab itself will be released and what data will be released. Well before the tab is due to be released you want to check that anonymisations and any speaker flags (i.e. Novice, ESL) are up to date in your tab software.

Managing the tab release
------------------------

Almost there!

If hosting Tabbycat on Heroku it's worth increasing the resources available to the server for the ~12 hour period following tab release; it's by far the most concentrated burst of traffic the site will receive. Because Heroku bills by the hour, even going to a relatively expensive option, such as performance dynos with auto-scaling, will be very cheap if run just for this period. That said the site should be relatively resilient even in the face of large amounts of traffic; even running with the most basic resources allocated, at worst pages will be temporarily slow or not load.

To get an idea of how the site is performing in the Heroku dashboard keep an eye on the average request time number and adjust the number of dynos to try and keep it under say two seconds; ideally just one. When you first turn on the tab release settings, make sure you go through and load every page before announcing it to the public, doing so will trigger the caching mechanism that means potentially complex pages (say the speaker tab) don't need to be calculated from scratch each time someone loads the page.

Post-tournament
---------------

Once you have sufficiently recovered, consider writing up and sharing a post-script about how things went; noting things that did or didn't go well. Next year's tab directors would certainly appreciate it, and it would be great to see this kind of knowledge spread more widely. The developers of your tab software would also appreciate hearing your feedback; particularly if there were issues that could have been prevented or ameliorated by the software itself.

Appendix: Briefing Notes
========================

This is a very loose, but not exhaustive, collection of things that are useful to communicate to speakers and adjudicators in a tab briefing. While briefing fatigue is real, having clear expectations about how things like ballots and feedback work are highly valuable uses of the tournament's time if they can at all help cut down the kinds of problems that delay the tab.

How feedback works
------------------

- Is it online, or offline? If online did people receive links? What do they do if they have lost it?
- Is feedback mandatory? What accountability mechanisms are there? Will you publish the shame list online or raise it in between rounds?
- Who will be submitting feedback on who? Do trainees do so?
- Remind teams that only one of their feedbacks count; they should coordinate who is doing it.
- What is the feedback scale? What does it correspond to? Common sources of confusion:

  - Feedback scales are not like Uber. You do not get five stars for being adequate and generic.
  - Feedback scales are not relative to position; it is an absolute scale. That is to say, if your trainee was good, they probably do not deserve the highest rating; they get whatever rating indicates they should be a panellist or low-chair.
  - Consider accompanying the score/scale with a statement characterising how these numbers correspond to positions - e.g. a 4.0 means 'should continue on good panels, should chair low rooms'

- If using online submission options, what should people without phones or internet access do?

How ballots work
----------------

This part of the presentation will be condescending. It is also necessary. The two causes of delays in the draw running late, and thus the tournament running late are (1) people not filling out ballots correctly or (2) people's ballots going missing. Emphasise that this should be taken seriously; minutes spent chasing bad ballots are often minutes that delay every single person at the tournament from doing what they are actually here to do. You should highlight, ideally with illustrated examples:

.. rst-class:: spaced-list

- Which parts of the ballot *must* be filled in; people will often overlook margins, or special fields such as motion vetoes.
- That people must specify the full names of speakers; not nicknames or just-first names. Often names will be written poorly or have ambiguities (i.e. two speakers on a team called James) and having the full name is the only way to resolve it.
- That people should **not draw arrows to swap the order of speakers** as these are impossible to decipher. Here, and in other areas, always *cross-out* information clearly and write it again rather than using arrows or drawing over what is there.
- That people should try and write numbers in a manner that makes them crystal clear. Put cross-bars in 7s; bases on 1's. Make 8's actually look like two circles. If people know they have poor handwriting maybe consider writing the literal words — *seventy-one* below the numbers.
- That for styles that do not have a single ballot for a panel, reiterate that everyone fills in their own ballots. At Australs, if this isn't made absolutely clear someone will average their panels ballots in order to try and 'help' you.
- That runners do not fill out ballots. In BP, remind them that only chairs should fill out ballots (i.e. it cannot be deputised to a wing). In formats with individual ballots, remind chairs to make sure their wings have actually filled out a ballot, and get them to check for errors or ambiguities.
- That everyone is bad at math. People who think they are good at math just haven't messed up their ballot *yet*. Emphasize that people should always use their phone's calculators to check totals. At typical tournaments using exclusively paper ballots math errors happen multiple times a round, almost every round.
- How long people have to fill out their ballots. Suggest that chairs actually keep track of this time during a stopwatch, and start moving towards critical steps (i.e. scoring) well *before* the time is up, not *once* it is up.
- Outline what chairs should do to return ballots. If ballots are being run by runners, outline what they should do if a runner doesn't appear. If they are not being run by runners remind people that returning ballots should be there number one priority, over say giving a lengthy adjudication or team feedback. Or getting lunch.
- Remind people to *be nice to runners* and that being mean to runners will have serious consequences.
- Remind people that the tab team and adjudication core will not, except for absolutely exceptional circumstances, accept photos or messaged descriptions of ballots; that all results must be on paper and handled in the same manner. The adjudication core should also be reminded of this.

How to locate the tab room
--------------------------

People should know how to get to the tab room, either to raise issues with the adjudication core or to correct ballot errors. Make it crystal clear where it is and how to get there. Also ensure people know not to barge in; that they should knock and wait.

Clearly communicate the contact details of the tab directors and get people to take them down. In most cases you do not want people going through convenors or the adjudication core for any tab-related issues.

Misc
----

Now is a good time to encourage people to consider getting involved with tabbing and tab-development. Emphasize that both do not necessarily require technical skills and that tabbers are (or should be) open to feedback and ideas from the wider community. Tell people to come find you and chat if they are interested and put up a link to the `Facebook tabbing group <https://www.facebook.com/groups/1681761898801915/?ref=bookmarks>`_.

If you appreciated this guide we'd appreciate a slide promoting `Timekept <http://timekept.com>`_ and `Debatekeeper <https://play.google.com/store/apps/details?id=net.czlee.debatekeeper&hl=en>`_. This would also be a good point to remind people that their timekeeping apps shouldn't be making noise *unless* they have been explicitly assigned to keep time by the chair.
