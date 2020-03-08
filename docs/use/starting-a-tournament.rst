.. _starting-a-tournament:

=====================
Starting a Tournament
=====================

This page outlines a few things you should do at the start of a tournament, after you've :ref:`imported the initial data <importing-initial-data>`. Once you've done these, proceed to :ref:`running a tournament <running-a-tournament>`.

.. caution:: Tabbycat is developed for — and tested on — modern web browsers. If you are using **Internet Explorer versions 8, 7, or 6** the interface may look odd or not function properly. Switch to a newer browser if possible.


Tournament configuration
========================

After importing all your data you can log into the site as an administrator by loading up the homepage and then using the **Login** button in the lower-right. From there you should go to the administration section of your tournament, and then go to the tournament configuration page by clicking **Setup** then **Configuration** in the menu.

Here you can adjust the debate rules and interface options to your liking then hit **Save** when finished. We also offer a number of presets that apply particular rule sets (such as the Australs rules) or feature sets (such as displaying information normally released during briefs on the website).

Special data types and options
==============================

There are a few optional fields that are not covered in the initial data templates, in the visual importer, or that may only be relevant in particular scenarios. It's worth going over these quickly to see if they are needed for your tournament. You can view and edit these fields in the **Edit Database** area (link is in the menu under the tournament's name).

Adjudicator Feedback > Adj Feedback Questions
  - As described in :ref:`adjudicator-feedback`, the types of questions that can be posed for adjudicator feedback are able to be heavily customised. If you are customising your feedback form it should be done here, and before the tournament starts.

Authentication and Authorisation > Users
  - Here you can add new admin users (those with full access) as well as new assistant users those (who can only do common data-entry tasks but not edit or view the full tab interface). See :ref:`user-accounts` for information on how to do this.

  .. note:: The people you're adding accounts for should be physically present when you do this, so that they can enter their password.

Participants > Regions
  - Optionally, each institution may belong to a *Region*. An institution's region is used within the adjudicator allocation process to visually identify teams and adjudicators for the purposes of highlighting diversity issues.  These have traditionally been used for geographic regions (such as Oceania), although could be repurposed as arbitrary markers of information — for example they could be used to denote teams from a particular State, institutional size, or circuit.

Participants > Adjudicators
  - An adjudicators *Base Score* represents their relative ability to judge important rooms, where adjudicators with higher numbers will, relative to the other adjudicators, be placed in better roles (ie as Chairs) and in the rooms you deem most important in each round. If you are running a small tournament, and plan to do your allocations manually, you can set everyone's number to the same amount.
  - For larger tournaments, particularly those that collect feedback, see the :ref:`adjudicator-feedback` section for more information on how base scores and other variables influence the automated allocation process.
  - Regardless of how you score the adjs, if you have changed the minimum chairing score in settings, you'll want to make sure there are enough adjudicators that meet this minimum threshold or the automated allocator may not function effectively.
  - All types of conflicts are assigned to the relevant adjudicator. Adjudicators can be conflicted against particular teams, particular institutions, and other adjudicators. Each of these is a located in a tab at the top of the page.
  - Each adjudicator's gender is optional and is not displayed publicly; it is only shown in the adjudicator allocation interface
  - Each adjudicator's pronoun is optional, and is only displayed if you use Tabbycat to print the ballots and feedback sheets for each round.

Participants > Teams
  - Note the distinction here between full name and short name. The latter is used on pages where space is tight, such as the draw displays or the adjudicator allocation interface.
  - Note that "Uses institutional prefix" option. With this option on, a team from the 'MUDS' institution named '1' or 'Gold' would be displayed as 'MUDS 1' or 'MUDS Gold'.
  - At present, setting a team's type to Bye, Swing, or Composite only affects very particular circumstances, and should be considered unnecessary.
  - If you do have composite teams, and wish to have them be conflicted by adjudicators from each respective instutution, you'll need to add a new team conflict to each adjudicator from each institution.
  - If you do have swing teams, or teams that are otherwise ineligible for breaking, this is typically handled through the breaks interface in the main site.

Participants > Speakers
  - Each speaker's gender is optional and is not displayed publicly; it is only shown in the adjudicator allocation interface.
  - Each speaker's pronoun is optional, and is only displayed if you use Tabbycat to print the ballots and feedback sheets for each round.

Tournaments > Tournaments
  - Note that tournaments can have a welcome message (useful for displaying maps and other information on the homepage).

Venues > Venues
  - A venue's priority determines its priority in being allocated. If there are 20 debates, and 30 rooms, the 20 rooms with the highest priorities will be chosen. Furthermore, if particular debates are marked as important during the draw process, those debates will receive the rooms with the highest priorities. In this way you can give close rooms to members of the adj core, or give larger rooms to debates that will draw a large audience.

Venues > Venue Categories
  - Venue categories are not needed for most kinds of tournaments. Their purpose is to classify particular venues, such as venues all within one building or venues that are accessible. Once assigned these categories can display in the venue's name — ie "Red 01.01" or be used to assign Venue Constraints that match particular teams, institutions, or adjudicators to particular types of venues.

Information for the briefing
============================

If you're using the online submissions feature, some things you should probably mention in the briefing:

- Adjudicators must fill out ballots completely, including motions and venues—they are entered into the system.
- There is a static URL for each person's ballots and feedback forms. It can be bookmarked, or the page can refreshed after each round.
- If people submit a result or feedback online, they should indicate that they have done so on the paper copy of their ballot.
