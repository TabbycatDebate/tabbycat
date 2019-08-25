.. _draw-generation:

===============
Draw Generation
===============

The draw generator is quite flexible. You can specify a number of settings to suit different tournaments' rules.

Summary of options
==================
Options are set in the **Configuration** page as described in :ref:`starting a tournament <starting-a-tournament>`.

.. list-table::
  :header-rows: 1
  :stub-columns: 1
  :widths: 20 40 40

  * - Option
    - Description
    - Allowable values

  * - :ref:`Odd bracket resolution method <draw-odd-bracket>`
    - How to resolve odd brackets
    - - Pull up from top
      - Pull up from bottom
      - Pull up from middle
      - Pull up at random

      If sides are `Random` or `Balance`:

      - Intermediate
      - Intermediate with bubble-up-bubble-down

      If sides are `Pre-allocated`:

      - Intermediate 1
      - Intermediate 2

  * - :ref:`Side allocations method <draw-side-allocations>`
    - How to allocate aff/neg
    - - Random
      - Balance
      - Pre-allocated
      - Manual ballot

  * - :ref:`Pairing method <draw-pairing-method>`
    - How to pair teams within brackets
    - - Slide
      - Fold
      - Adjacent
      - Random

  * - :ref:`Conflict avoidance method <draw-conflict-avoidance>`
    - How to avoid history/institution conflicts
    - - Off
      - One-up-one-down

  * - :ref:`Pullup restriction <draw-pullup-restriction>`
    - Whether and how to restrict pullups
    - - No restriction
      - Choose from teams who have been pulled up the fewest times so far
      - Choose from teams with the lowest draw strength by speaks so far

.. caution:: The valid options for intermediate brackets change depending on whether sides are pre-allocated, but these are **not** checked for validity. If you choose an invalid combination, Tabbycat will just crash. This won't corrupt the database, but it might be momentarily annoying.

The big picture
===============
When generating a power-paired draw, Tabbycat goes through five steps:

1. First, it divides teams into "raw brackets", grouping them by the number of wins.
2. Second, it resolves odd brackets, applying the odd brackets rule to make sure there is an even number of teams in each bracket. This is often called "pulling up" teams.
3. Third, within each bracket, it pairs teams into debates using the pairing method.
4. Fourth, if enabled, it adjusts pairings to avoid history or institution conflicts.
5. Finally, it assigns sides to teams in each debate.

For each of these steps except the first, Tabbycat allows you to choose between
a number of different methods.

Explanations of options
=======================

.. _draw-odd-bracket:

Odd bracket resolution
----------------------
The **draw odd brackets** option specifies what you do when a bracket has an odd number of teams. (Obviously you have to do something, otherwise you can't pair off teams within the bracket.) There are two groups of methods: pull-up and intermediate brackets.

.. rst-class:: spaced-list

- **Pull-up methods** take one or more teams from the next bracket down, and move them into the odd bracket to fill the bracket.

- **Intermediate brackets** take the excess teams from the odd bracket and move them down into a new bracket, which sits between the odd bracket and the next one down (the "intermediate bracket"). It then takes teams from the next bracket down and moves them up to fill the new intermediate bracket.

The exact mechanics depend on whether or not sides are pre-allocated.

When sides are not pre-allocated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. rst-class:: spaced-list

- **Pull-up methods:** Take a team from the next bracket down, and add them to the odd bracket to form an even bracket. You can choose to pull up the top team from the next bracket, or the bottom team, or the middle team, or a randomly chosen team. (If you pull up the middle team, and the bracket has an even number of teams, then it will choose randomly from the two middle teams.)

- **Intermediate brackets:** Take the bottom team from the odd bracket and match them against the top team from the next bracket. An intermediate bracket always has two teams.

  If you're using conflict avoidance and intermediate brackets, you will probably want to use **Intermediate with bubble-up-bubble-down** instead. This uses the "bubble-up-bubble-down" rule to swap teams out of an intermediate bracket if there is a history or institution conflict. This is defined in the Australs constitution and is analogous to the "one-up-one-down" rule.

.. caution:: Using `Intermediate` with `One-up-one-down` does **not** imply `Intermediate with bubble-up-bubble-down`. You must enable `Intermediate with bubble-up-bubble-down` specifically.

When sides are pre-allocated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When sides are pre-allocated, an "odd bracket" is one that has an uneven number of affirmative and negative teams. (So odd brackets can have an even number of teams, *e.g.* 4 affs and 2 negs.)

.. rst-class:: spaced-list

- **Pull-up methods:** Take as many teams from the next bracket down as necessary to fill the bracket. If there aren't enough teams in the next bracket down, take teams from the bracket after that, and so on, until the (original) odd bracket is filled. Higher brackets are always filled first. You can choose to pull up the top teams from the next bracket, the bottom teams, or a random selection of teams.

- **Intermediate brackets:** Take the unpaired teams in a bracket, and move them down to a new intermediate bracket. Then, take the number of teams necessary from the opposite side, from the next bracket down, to fill the next bracket.

  **Intermediate 1** and **Intermediate 2** differ only in what happens if there aren't enough teams in the next bracket to fill the intermediate bracket. In **Intermediate 1**, it will just take teams from the bracket after that, and so on, until the intermediate bracket is filled. In **Intermediate 2**, it will split the intermediate bracket: the teams that can be paired with the next bracket form the first intermediate bracket, and then the teams that aren't form a new (unfilled) intermediate bracket, to be filled from teams from the bracket after that. This keeps going, splitting into as many intermediate brackets as necessary, until all excess teams from the original odd bracket are paired.

.. _draw-side-allocations:

Side allocations
----------------
There are four methods:

.. rst-class:: spaced-list

* **Random** allocates randomly. Some tournaments might like this, but most will probably want to use Balance, because Random doesn't guarantee that a team won't be (say) affirming the entire tournament.
* **Balance** assigns the team that has affirmed less so far the affirmative side (and, therefore, the team that has negated less the negative side). If both teams have affirmed the same number of times, it assigns sides randomly.
* **Preallocated** is used for pre-allocated sides. If used, you must enter data for pre-allocated sides into the database, as specified below.
* **Manually enter from ballot** is used for tournaments where the sides of the teams involved are not assigned in advance, but are instead determined by the teams themselves

Pre-allocated sides
^^^^^^^^^^^^^^^^^^^
There isn't currently any way to edit side allocations from the front end. To do so from the back end, you need to create one ``TeamPositionAllocation`` entry for each team in each round. All teams must have an allocation for every round. There are a few ways to do this, take your pick:

.. rst-class:: spaced-list

* If you're using the :ref:`importtournament command <importtournament-command>`, it reads sides from the file sides.csv.
* You can do this from the Django admin interface (under Setup > Edit Database) by going to the relevant team and adding a **team position allocation** entry. That is:

  #. Click **Admin** on the bottom right of any page after logging into an account with :ref:`superuser access <user-accounts>`.
  #. Next to **Teams**, click **Change**.
  #. Click on the name of the team you want to edit side allocations for.
  #. Add or edit the entry or entries in the **Team position allocations** table at the bottom.

* You can also do this by writing a script that creates ``TeamPositionAllocation`` objects and saves them. Have a look at `draw/management/commands/generatesideallocations.py <https://github.com/TabbycatDebate/tabbycat/blob/master/tabbycat/draw/management/commands/generatesideallocations.py>`_ for an example.

.. _draw-pairing-method:

Pairing method
--------------
It's easiest to describe these by example, using a ten-team bracket:

* **Fold**: 1 vs 10, 2 vs 9, 3 vs 8, 4 vs 7, 5 vs 6. (Also known as high-low pairing.)
* **Slide**: 1 vs 6, 2 vs 7, 3 vs 8, 4 vs 9, 5 vs 10.
* **Adjacent**: 1 vs 2, 3 vs 4, 5 vs 6, 7 vs 8, 9 vs 10. (Also known as high-high pairing.)
* **Random**: paired at random within bracket.

Teams are always paired within their brackets, after resolving odd brackets.

.. _draw-conflict-avoidance:

Conflict avoidance method
-------------------------
A **conflict** is when two teams would face each other that have seen each other before, or are from the same institutions. Some tournaments have a preference against allowing this if it's avoidable within certain limits. The **draw avoid conflicts** option allows you to specify how.

You can turn this off by using **Off**. Other than this, there is currently one conflict avoidance method implemented.

**One-up-one-down** is the method specified in the Australs constitution. Broadly speaking, if there is a debate with a conflict:

* It tries to swap teams with the debate "one up" from it in the draw.
* If that doesn't work, it tries to swap teams with the debate "one down" from it in the draw.
* If neither of those works, it accepts the original conflicted debate.

It's a bit more complicated than that, for two reasons:

.. rst-class:: spaced-list

* History conflicts are prioritised over (*i.e.*, "worse than") institution conflicts. So it's fine to resolve a history conflict by creating an institution conflict, but not the vice versa.
* Each swap obviously affects the debates around it, so it's not legal to have two adjacent swaps. (Otherwise, in theory, a team could "one down" all the way to the bottom of the draw!) So there is an optimization algorithm that finds the best combination of swaps, *i.e.* the one that minimises conflict, and if there are two profiles that have the same least conflict, then it chooses the one with fewer swaps.

.. _draw-pullup-restriction:

Pullup restriction
------------------
You can restrict which teams can be pulled up by configuring the draw generator to choose a pullup team from among only those teams who are the "best off" according to a given metric. If several teams are equally "best off" within the lower bracket, the draw generator chooses among them using the same **pull-up method** already specified (*e.g.*, "pull up from top")

.. rst-class:: spaced-list

* You can **choose from teams who have been pulled up the fewest times so far**, that is, in rounds before the current round. Most of the time, this is equivalent to saying that a team cannot be pulled up more than once. But if *all* teams in a bracket have been pulled up at least once, it then chooses from among teams who have been pulled up *only* once (if any), and so on.

* You can **choose from teams with the lowest draw strength so far**, by **wins** or **speaks**.

  If you choose speaks, it's unlikely that two teams will have the same draw strength by speaks, so most of the time this will just choose the team in the lower bracket that's had the easiest draw so far (as measured by their opponents' speaker scores).

Pullup restrictions only apply when the :ref:`odd bracket resolution method <draw-odd-bracket>` is a pullup method. They have no effect on intermediate brackets.

What do I do if the draw looks wrong?
=====================================

You can edit match-ups directly from the draw page. Functionally, you can do anything you want. Of course, operationally, you should only edit the draw when you *know* that the draw algorithm got something wrong. If you need to do this, even just once, please file a bug report by creating a new issue on `our issues page on GitHub <https://github.com/TabbycatDebate/tabbycat/issues>`_.
