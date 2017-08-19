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
|                         | entropy               | (default: **1**, *i.e.*           |
|                         |                       | Shannon entropy)                  |
+-------------------------+-----------------------+-----------------------------------+
| **Position cost**       | Degree to which large | Any non-negative number           |
| **exponent**            | position imbalances   | (default: **4**)                  |
|                         | should be prioritized |                                   |
+-------------------------+-----------------------+-----------------------------------+
| **Assignment method**   | Algorithm used to     | - `Hungarian`\*                   |
|                         | assign positions      | - **Hungarian with preshuffling** |
+-------------------------+-----------------------+-----------------------------------+

The big picture
===============

To try to achieve position balance, Tabbycat treats the allocation of teams to debates as an `assignment problem <https://en.wikipedia.org/wiki/Assignment_problem>`_. That is, it computes the "cost" of assigning each team to each position in each debate, and finds an assignment of all teams to a position in a debate that minimises the total cost (the sum over all teams).


Explanations of options
=======================

Pullup distribution
-------------------

If the number of teams in a bracket is not a multiple of four, it pulls up teams from the next bracket down. The pullup distribution then governs how those teams are paired into the upper bracket.

The available options are as follows:

* **Anywhere in bracket:** The pullup teams are treated as if they were any other team in their new bracket. For example, if there are 17 teams in a 10-point bracket, then the three 9-point teams that get pulled up may be paired anywhere in the 10-point bracket, independently of each other. Chance might put them in the same room, but more likely, they will not all be in the same room, so there will be multiple pullup rooms in the 10-point bracket.
* **All in the same room:** All of the pullup teams will be paired into the same room. This means that there will be at most one pullup room per bracket, effectively creating an "intermediate bracket".

.. note:: While it can be argued that the `All in the same room` setting is fairer, it is prohibited by the WUDC constitution. If your tournament follows WUDC rules, you cannot use this setting.

Position cost options
---------------------

The `position cost function` is a function that indicates how "bad" it would be if a team were to be allocated a certain position (OG, OO, CG, CO) in a debate. When generating a draw, Tabbycat chooses from among the draws that minimise the sum of the position costs for each team.

More formally:

* A `position history` or just `history` :math:`\mathcal{H}` is a 4-tuple where each element is the number of times a team has already been in the corresponding position.
* A cost function :math:`C(\mathcal{H},s)` is a function specifying how "bad" it would be if a team with position history :math:`\mathcal{H}` were assigned the position :math:`s` in the next round.

Tabbycat allows you to choose from a number of different **position cost functions**, as well as a **position cost exponent** :math:`\beta`. Then, when allocating teams to debates, Tabbycat allocates teams to positions :math:`(s_t, t \in\mathcal{T})` to minimise

.. math::

  \sum_{t \in \mathcal{T}} [C(\mathcal{H}_t,s_t)]^\beta

where :math:`\mathcal{T}` is the set of all teams, :math:`\mathcal{H}_t` is the position history of team :math:`t` and :math:`s_t` is the position to which team :math:`t` would be allocated.

Position cost exponent
^^^^^^^^^^^^^^^^^^^^^^

The position cost exponent :math:`\beta` controls how different teams trade off with each other.

The larger :math:`\beta` is, the more concerned it is with preventing `very` bad situations. That is, it will give more teams some slight unevenness in order to prevent one team from getting a `very` uneven history. At the extreme, as :math:`\beta\rightarrow\infty`, it will do everything it can to minimise the plight of the `worst-off` team, and it won't care for `any` team other than the worst-off.

The smaller :math:`\beta` is, the more concerned it is with preventing `any` unevenness. That is, it will try to keep more teams from being uneven `at all`, at the cost of possibly letting just one team get a very uneven history. At the extreme, as :math:`\beta\rightarrow\zero`, it will do everything it can to minimise the number of teams with a non-optimal profile---but if it can't keep `everyone` even, then it won't care exactly `how` uneven the unlucky teams get.

The "balanced" approach would be :math:`\beta = 1`, which just takes the cost function as-is. This doesn't mean that this is the best idea, however---you'd typically want to bias towards preventing very uneven histories a bit more. Most tournaments will probably what :math:`\beta` to be somewhere between 2 and 5.  (Note that :math:`\beta` need not be an integer.)


Position cost functions
^^^^^^^^^^^^^^^^^^^^^^^

Simple
""""""


Rényi entropy
"""""""""""""


Population variance
"""""""""""""""""""


Assignment method
-----------------

