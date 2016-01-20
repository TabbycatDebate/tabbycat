.. _data-entry:

=============================
Entering ballots and feedback
=============================

Ballot checkin
==============

For tournaments that require it, there is a "ballot checkin" page that can be used to record the arrival of ballots to the tab room. When there's a missing ballot, it can help establish whether the ballot never made it to the tab room, or whether it's probably floating around in the room forgotten. Also, it can help enforce early checks that panels return the correct number of ballots to the room.

To get to the ballot checkin, click the relevant round at the top right of the Tabbycat admin interface, and then click "Ballot checkin". This requires superuser privileges.

There's no adverse effect from not using the ballot checkin. Data enterers will still be able to enter and confirmed ballots, even if not checked in.

.. tip::

  - Since the ballot checkin tends to require a dedicated computer or two, it can be worth creating a separate superuser account for ballot checkin, so that it doesn't appear on the action logs as being by a particular person.
  - Don't forget to provision a computer or two for this if you're planning to use it.
  - Ballot checkins can be a bottleneck, so you might decide they're not worth using. Alternatively, you might have multiple computers for this purpose, or you might dedicate a tab room helper to driving the process (since this is probably faster than runners doing the typing in turn).

Ballot entry
============

Most tab rooms run some sort of check system to ensure data is entered accurately. In Tabbycat, this is built into the system, which also helps speed it up.

As a general principle, Tabbycat requires all ballots to be looked at by two people. The first person enters the data from the ballot, and the second person checks it. The second person isn't allowed to modify the data—they either confirm it or reject it, and if they reject it, then the whole process starts again. This is by design: to be confirmed, the *same* data must have been seen by at least two people.

.. caution:: The Tabbycat admin interface does **not** work like this. It's designed to be flexible, so allows you to edit, confirm or unconfirm any ballot at any time. For this reason, you should **not** use the Tabbycat admin interface for general data entry. If a tab director or adjudication core member will be entering data, they should have a separate account for this purpose.

.. tip::

  - Don't forget to check the totals against the ballot—they're a useful integrity check too.
  - Don't forget to check the winner against the ballot! If the adjudicator gets it wrong, it's worth asking to clarify.
  - It can be helpful to think about the room layout to maximize efficiency.
  - Some tab rooms like to assign some to data entry and some to verification. This isn't really necessary, since Tabbycat doesn't let the same person enter and verify the same ballot. (This is one of many reasons why every person should have their own account.)

Feedback entry
==============

Feedback doesn't have the same verification process as ballots. Feedback that is entered by the tab room is assumed to be confirmed. If feedback is entered multiple times, all copies are retained but only the last one "counts" (is considered confirmed).

Online ballot submissions
=========================

.. todo:: We haven't written this documentation yet.

Online feedback submissions
===========================

.. todo:: We haven't written this documentation yet.
