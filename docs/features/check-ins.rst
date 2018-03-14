.. _check-ins:

=========
Check-Ins
=========

A 'Check-in' is a record of a speaker or adjudicator's presence at a particular point in time. Typically these are used at large tournaments to reliably track who is or is not present for the first round of each day.

Check-ins serve a similar purpose to the :ref:`availability <availability>` system. However availabilities are tied to a particular round rather than a particular time, and so can be used to record instances where you know ahead of time whether a person should be included in the draw, or to exclude someone from a draw even though they are present. That said, the availability allows you to easily mark adjudicators or teams who have checked-in as available for a given round.

Check-In Identifiers
====================

Check-ins are associated with a 'identifier' — a number that is unique to each speaker and adjudicator. To generate these numbers go to the *Identifiers* section under the Check-Ins menu. From here you generate identifiers for Speakers, Adjudicators, and Venues as needed. Note also that Identifiers can be manually added or edited in the *Edit Database* area if necessary.

.. image:: images/check-ins-overview.png

Once this number has been generated it can be transformed into a barcode so that it can be easily included on tournament badges or otherwise printed and disbursed. On the same *Identifiers* page you can use the *View barcodes* option to open up a page that lists all the barcodes for the speakers, adjudicators, or venues.

.. image:: images/barcodes.png

.. note:: The identifiers for ballots are automatically generated when printing ballots.

Recording Check-Ins
===================

On the *Scanning* section of Check-ins you can record a particular check-in. This can be done in a few different ways:

1. You can type in the Identifier number into the box. Once five numbers have been identified it will automatically issue the check-in and clear the input field for the next number.

2. If you have purchased barcode scanners and configured them as USB keyboards they should then be compatible with this page. I.E. upon page load the cursor should be positioned in the input field, and any scanned barcodes should populate it with the specified number, issue the check-in, and then clear the box for the next scan.

3. If your device has a (web)cam you can use the Scan Using Camera button. Any barcodes put in front of the camera's video stream will be scanned into the form.

    .. image:: images/checkin_live.png


    .. note:: Camera scanning works on most modern browsers although it will only work with Safari 11 or higher (iOS 11+ and macOS 10.13+). Camera scanning may also not work when using a local-installation of Tabbycat in all browsers, *except* Firefox. Depending on the quality of your camera barcodes that are less than 4cm wide may not be recognised — ideally barcodes should be at least 5cm if using this method as your main way of checking-in things.

4. The Check-in status page (described below) allows assistants and administrators to manually check-in particular people or entire institutions without needing to know their identifiers.

The Check-In 'Window'
=====================

Because Check-In events are not explicitly linked to rounds you should consider how long it takes for a check-in to be considered valid. The time of this 'window' in hours can be set in *Setup* > *Configuration* > *Data Entry*.

At tournaments where you want to run a check-in process at the start of each round you may want to set the time to around 2 hours. At tournaments the run check-ins during the start of each day the check-in 'window' (i.e. the time before check-ins expire) should be set at around 12 hours or more — enough time to distinguish between the first check-ins of that day as compared to the last check-ins of the previous day.

Viewing Check-Ins
=================

On the *People Statuses* section of Check-ins you can view who has or has not been checked-in. This page will live-update with the latest check-ins so you should be able to leave it open to monitor income attendances.

.. image:: images/checkin_statuses.png

The blue "tick" boxes allow you to manually check-in people and/or entire institutions (for *People*) or venues and/or venue groups (for *Venues*) , without the need to scan their identifiers. This style of check-in is designed for use an auditorium roll-call type situation where you might be running through a list of people to the room or identifying absences on a per-institution basis.

    .. note:: Viewing ballot check-ins is done on the *Results* page for that round.
