.. _running-a-tournament:

====================
Running a Tournament
====================

Once you've finished the steps in :ref:`starting-a-tournament`, you're ready to go! This page outlines what you would do for each round during the tournament. After the tournament, proceed to :ref:`finishing-a-tournament`.

This is all done from an admin interface (*i.e.*, by the tab director or adjudication core member). In the admin interface, tournament-wide pages (feedback, standings, and break) are at the top of the left-hand menu, while round-specific pages (check-ins, draw, display, motions, and results) are in dropdown's organised by each round;s abbreviation.

The basic workflow for each round is:

#. :ref:`Check-in the teams, adjudicators, and venues present <check-ins>`
#. :ref:`Generate the draw <generating-the-draw>` and allocate the adjudicators
#. :ref:`Show/release the draw <releasing-the-draw>`
#. :ref:`Release/enter <releasing-the-motions>` the motions
#. Have the debates
#. :ref:`Enter results <entering-results>`
#. :ref:`Advance to the next round <advancing-round>`

.. _check-ins:

Check-ins
=========

**Set availability.** For each round, you need to set the venue, team and adjudicator availability. If any of those are not marked as available they will not be used within the draw; so this feature is mostly useful for when adjudicators or venues are only available for certain rounds.

To do this, click the round in the menu, then click **Check-Ins**. Here you can then go to the availability pages for venue, teams, and adjudicators, or check in everything at once. When you've set everything appropriately use the **Generate Draw** button in the top right to advance.

  .. image:: images/checkins-page.png

.. _generating-the-draw:

.. note:: You can set availabilities in advance of the current round — ie if you know the venue/adjudicator schedules their availabilities can be set ahead of time.

Generating the draw
===================

1. **Confirm the draft draw**. After advancing from availability section you will first be shown a draft draw that details how the draw was formulated, pointing out pull-ups and conflict swaps and the like.

  .. image:: images/draft-draw.png

.. note:: The draft draw is for you to double-check. While there are some basic tests on the draw algorithm, it never hurts to sanity-check it again.

    If you *do* find something wrong with a draft draw, you can edit the match-ups, but please also let us know what the problem was! You can find our contact details in the :ref:`authors` section.

2. Once on the confirmed draw page you can click **Edit Adjudicators**.

  .. image:: images/draw-without-adjs.png

3. **Allocate the adjudicators**. Changes here will auto-save; feel free to return to the **Draw** when needed. See :ref:`adjudicator allocation <adjudicator-allocation>` for more details about the allocation process.

  .. image:: ../features/images/adj-allocation.png

.. note:: If you are using venue constraints the **Draw** page may prompt you to Auto Allocate the venues used to satisfy those constraints; see :ref:`venue-constraints <venue-constraints>` for more details. Regardless of whether you are using venue constraints or not you can change the Venues per-debate in the **Edit Venues** area.

.. _releasing-the-draw:

Releasing the draw
==================

Once you're happy with your adjudicator allocation, you're ready to start the round.

1. **Release to general assembly.** From the *Display* page for that round, go to **Show by Venue** or **Show by Team** (whichever you prefer). Then put it up on the projector. There are automatic scroll buttons and buttons for changing text sizing.

  .. image:: images/draw-by-venue.png

2. **Release to public.** If you're using the public draw function (where the draw is posted publicly to your Tabbycat website) use the **Release to Public** button to allow the page to display.

  .. tip:: To avoid the site from being overloaded by anxious refreshers, we recommend that large tournaments not release the draw to the public until after it's been seen by general assembly.

.. _releasing-the-motions:

Entering and Releasing Motions
==============================

Tabbycat is agnostic as to whether you enter motions into Tabbycat before or after they are shown publicly. However, they must be entered *at some point* before ballots are entered.

1. **Enter the motion text.** Either before or after their public release motions can be entered in the **Motions** section for that round.

2. **Release to general assembly.** If you are entering motions *before* they are publicly revealed note that there is a *Display Motions* button in the **Display** area that allows you to do a Power Point style motion release.

3. **Release to public.** As with draws, if you have the *enable public view of motions* setting configured your Tabbycat website will display a running list of motions from the tournament. When this is on, using the **Release Motions to Public** button on the **Motions** page will mark the current set of motions as able to be displayed on this page.

.. _entering-results:

Entering Results
================

1. Enter debate results and feedback as they come in (and/or allow online entry of results and feedback).

2. Both results and feedback entered in the tab room or online need to be confirmed before the results are counted. To confirm a debate ballot and the debate as a whole, the confirmed checkbox under *Ballot Status* should be ticket in addition to the *Debate Status* being set to Confirmed.

3. Note that you can track data entry progress from the **Overview** page in an admin account (get there by clicking the tournament's name in the menu).

See :ref:`data-entry` for more details about the data entry process.

.. warning:: For major tournaments, we don't recommend entering any data from an admin's account. This is because the admin interface (intentionally) does not enforce the data confirmation procedure.

.. _advancing-round:

Advancing to the next round
===========================

Once you've got all the results entered and confirmed, you're ready to progress to the next round. This can be done by going to the **Results** area, and then using the **Advance to Next Round** button.

.. image:: images/results-page.png

.. warning:: When you advance to the next round, if you've enabled public results, the results for the current round (which is now the previous round) will be release to the public **unless** the round is marked as "silent" in the database. So if you're careful about when results should be released, don't change the current round until you're ready to release those results.

.. note:: There is a design assumption that you will always want to release results for non-silent rounds before you start working on the draw for the next round. If this isn't true for you, please get in touch with us so that we know. The workaround is to make all rounds silent, then unsilent them when you're ready to release results.
