====================
Draw Generation (BP)
====================

The draw generator for British Parliamentary tournaments tries to rotate teams through positions by assigning them positions they've been in less often before the current round.

Summary of options
==================

Options are set in the **Configuration** page as described in :ref:`starting a tournament <starting-a-tournament>`. Options in `italics` with an asterisk are not WUDC-compliant. The recommended options are shown in **bold**.

+-------------------------+-----------------------+-----------------------------------+
|          Option         |      Description      |          Allowable values         |
+=========================+=======================+===================================+
| **Pullup distribution** | Where pullup teams    | - **Anywhere in bracket**         |
|                         | get placed            | - `All in the same room`\*        |
+-------------------------+-----------------------+-----------------------------------+
| **Position cost**       | Which cost function   | - Simple                          |
|                         | to use to indicate    | - **Rényi entropy**               |
|                         | which position        | - Population variance             |
|                         | profiles are          |                                   |
|                         | preferred             |                                   |
+-------------------------+-----------------------+-----------------------------------+
| **Rényi order**         | Order of Rényi        | Any non-negative number           |
|                         | entropy               | (default: 1, *i.e.*               |
|                         |                       | Shannon entropy)                  |
+-------------------------+-----------------------+-----------------------------------+
| **Position cost**       | Degree to which large | Any non-negative number           |
| **exponent**            | position imbalances   | (default: 4)                      |
|                         | should be prioritized |                                   |
+-------------------------+-----------------------+-----------------------------------+
| **Assignment method**   | Algorithm used to     | - `Hungarian`\*                   |
|                         | assign positions      | - **Hungarian with preshuffling** |
+-------------------------+-----------------------+-----------------------------------+

The big picture
===============

To try to achieve position balance, Tabbycat treats the allocation of teams to debates as an `assignment problem <https://en.wikipedia.org/wiki/Assignment_problem>`_. That is, it computes the "cost" of assigning each team to each position in each debate, and finds an assignment of all teams to a position in a debate that minimizes the total cost (the sum over all teams).


Explanations of options
=======================

Pullup distribution
-------------------

If the number of teams in a bracket is not a multiple of four, it pulls up teams from the next bracket down. The pullup distribution then governs how those teams are paired into the upper bracket.

* If `Anywhere in bracket` is selected, then the pullup teams are treated as if they were any other team in their new bracket. For example, if there are 17 teams in a 10-point bracket, then the three 9-point teams that get pulled up may be paired anywhere in the 10-point bracket, independently of each other. Chance might put them in the same room, but more likely, they will not all be in the same room, so there will be multiple pullup rooms in the 10-point bracket.
* If `All in the same room` is selected, then all of the pullup teams will be paired into the same room. This means that there will be at most one pullup room per bracket, effectively creating an "intermediate bracket".

.. note:: While it can be argued that the `All in the same room` setting is fairer, it is prohibited by the WUDC constitution. If your tournament follows WUDC rules, you cannot use this setting.

Position cost
-------------

Simple
******


Rényi entropy
*************


Population variance
*******************


Assignment method
-----------------

