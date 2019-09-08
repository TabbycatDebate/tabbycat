.. _preformed-panels:

================
Preformed Panels
================

Preformed panels, also known as a 'shadow draw', allow for adjudicator panels to be created *before* a round has been drawn and then applied once its draw is ready. This means that the task of panel formation can be largely performed during periods that sit outside of the normal time pressure that comes with trying to finalise a draw for release. This process can save significant amounts of time at large tournaments, or at tournaments where the adjudication core wants to very carefully control the specific combination of adjudicators within panels.

Tabbycat's implementation of preformed panels is more powerful, but less intuitive, than many other implementations. The chief difference is that our workflow does not simply transpose a linear set of preformed panels atop a draw. Instead we employ Tabbycat's existing allocation tools, primarily the notion of a debate's *priority*, to allow for a non-linear matching of preformed panels that will avoid creating conflicts and can better adapt to a given draw and — particularly when the most important debates do not strictly follow the highest debate brackets.

The central concept here is that each preformed panel has a specific priority value. When applying preformed panels to a draw, the allocator ties to best match the priority value of each preformed panel to the priority of each actual debate. This is approximately equivalent how Tabbycat's normal auto-allocator matches the strength of each potential panel (as measured by adjudicator's ratings) to the priority (or as a fallback: the bracket) of each debate.

Step 1: Creating Preformed Panels
=================================

The link to the preformed panels section is available under the **Setup** menu. Preformed panels are formed for specific rounds, and this page links to all of the rounds available in your tournament. The page for creating preformed panels for a specific round is essentially the same as that of the normal adjudicator allocation.

.. note:: The **Draw** page of each individual round also contains direct linked to the preformed panels of that specific round and the next round.

Initially, the preformed panels page will have no panels available. The **Create Panels** button in the top-left will let you make some. Note that the panels it creates are based upon a projection of that round's general results using the results of the previous round. As a result, each preformed panel will have a bracket-range and a liveness range.

.. image:: images/preformeds-create.png

.. note:: Like the normal adjudicator allocation interface, the preformed panel interfaces will indicate when an adjudicator has not been marked as available. If using preformed panels, you may want to set adjudicator availability earlier than you would otherwise.

Step 2: Assign Priorities to Preformed Panels
=============================================

By default the priority slider for all preformed panels is in the neutral position. You can use the "Prioritise" button in the top left to assign each preformed panel an priority value automatically based upon their brackets or liveness. Before or after this step you can alter the priorities as normal — even after you have allocated adjudicators.

It is, important, to remember to assign a range of priorities to the panels. Without distinct priority values, the application of your preformed panels to the actual draw will be essentially random. If allocating priorities manually, it is a good idea to keep a relatively even distribution of preformed panel priorities — use the range!

.. note:: In Round 1, each debate has a liveness and bracket of 0. If you are using preformed panels in this instance you may need to manually-differentiate their priorities.

Step 3: Allocate Adjudicators to Preformed Panels
=================================================

.. image:: images/preformeds-allocate.png

Now that your panels have an priority, you can begin allocating adjudicators. This can be done entirely manually; however note that the normal 'auto' allocator also functions in this context. Even if you want to tweak your panels extensively, the auto-allocator can provide a good first-pass collection of panels because it will give stronger adjudicators to the panels that you have marked as important. It will also avoid creating conflicts in forming its panels.

The created panels all autosave, so you can leave the page as needed. Like the main allocation interface, changes should appear 'live' across different computers and the sharding system is available to divide up each person's view of the draw.

Step 4: Create the Draw
=======================

Proceed with the creation of the draw as per normal. Open up the normal adjudicator allocation page for that round.

Step 5: Assign Priorities to the Debates
========================================

When allocating preformed panels, the system uses priority is the interface between the preformed panels and the actual debates. It is thus crucial that you assign priorities to the debates in the actual draw using automatic prioritisation or the manual sliders. Because the automatic prioritiser does not employ the highest priority value, it is worth having a look at the draw and seeing if any debates justify this before proceeding.

Step 6: Allocate Preformed Panels to Debates
============================================

To allocate preformed panels to your debates you click the 'normal' Allocate button and then select the *Preformed Panels* option.

.. image:: images/preformed-apply.png

This will then automatically apply those preformed panels.

.. image:: images/preformed-done.png

You can the edit the allocation as normal. If needed, you can redo the allocation of the preformed panels at any point.
