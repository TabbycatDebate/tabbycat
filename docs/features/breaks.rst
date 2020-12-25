.. _breaks:

=========================
Breaks and Break Rounds
=========================

In Tabbycat, elimination rounds (sometimes called *outrounds* or the *final
series*) are called "break rounds", and the qualification of teams to compete in
the elimination phase of a tournament is called the "break".

About break categories
======================

Tabbycat supports multiple and arbitrarily-named break categories. Most
tournaments will have just one category, typically called "Open", leading to the
grand final. Some tournaments also have restricted-eligibility break categories,
for example, for novice teams or teams for whom English is a second language.

Having multiple break categories is intended for tournaments where multiple
*parallel* elimination phases derive from the *same* preliminary rounds
(inrounds). It's not for parallel but distinct competitions---for those, you
should create distinct tournaments.

.. _breakqual-rules:

Break qualification rules
-------------------------

Tabbycat supports several break qualification rules, and each break category
must be configured to use one of them. Most tournaments will use "Standard",
which is the default.

.. list-table::
  :header-rows: 1
  :stub-columns: 1
  :widths: 30 70

  * - Rule name (string to use in ``importtournament`` CSV files)
    - Description

  * - Standard (``standard``)
    - The top *n* teams break. This is the default, and
      most tournaments use this rule.

  * - AIDA 1996 (``aida-1996``)
    - The top *n* teams that are also in the top three teams
      from their institution break.

  * - AIDA 2016 (Australs) (``aida-2016-australs``)
    - The top *n* teams that fulfil either of these criteria
      break:

      - They are in the top *n* teams overall, and in the top three teams from
        their institution.
      - They have at least as many wins as the *n*\ th-ranked team, and they are
        the top team from their institution.

      If fewer than *n* teams fulfil either criterion, then
      the best teams not fulfilling the criteria are added to
      make *n* teams.

  * - AIDA 2016 (Easters) (``aida-2016-easters``)
    - As for AIDA 2016 (Australs), except that if fewer than
      *n* teams fulfil either criterion, then only the best
      teams who are in the top three teams from their
      institution are added to make *n* teams.

.. note:: The break generators are somewhat more complex than described in the
  above table: among other things, they also handle cases where there is a tie
  for the last place in the break, and for those break categories marked
  "general", they will show where ineligible teams would have broken, had they
  been eligible.

Setting up break categories and rounds
======================================

For each break category in your tournament, you need to do two things:

  1. Create (and name) a break category
  2. Set the eligibility of teams to compete in the category

If you only have one break category (open) and you create your tournament using
the "Create New Tournament" page, simply enter the number of teams in the break
(*e.g.*, 8 if you're breaking to quarterfinals). Tabbycat will create the break
category and break rounds for you. For any further break categories, you'll need
to go to the **Breaks** item in the left-hand menu for a particular tournament
and then click **Break Categories**. Fill out the forms for the number of new
break categories and save. Rounds will be created automatically. You'll still
need to set the eligibility of teams though, as in (3) below.

If you create your tournament using the `importtournament` command or in **Edit
Database**, you'll need to do all three steps above yourself. You may also want
to edit the break rounds (2) to change their names.

1. Creating break categories
----------------------------

If using the `importtournament` command, there is an example file,
*break_categories.csv*, that you can copy and adjust. If using **Edit Database**,
add categories under **Break Qualification > Break categories**.

Most of the fields are self-explanatory or described on the Edit Database form,
except for one: "rule", which sets the break qualification rule. Permissible
values are described in :ref:`breakqual-rules` above. If using
`importtournament`, be sure to use the correct string (in brackets in the
table). The rule defaults to "Standard" (``standard``).

.. note:: The "institution cap" field was removed in Tabbycat 1.0. All Australs
  break qualification rules are now hard-coded to a cap of three teams per
  institution.

2. Creating break rounds
------------------------

You should create a round for every break round you intend to hold, including
it in *rounds.csv* if using `importtournament`, or adding them under
**Tournaments > Rounds** if using **Edit Database**. Be careful to set the
following fields correctly:

- *Break category* must be set to the relevant break category.
- *Stage* and *draw type* must both be set to "Elimination".

3. Setting break eligibility
----------------------------

Once a break category has been created it will not have any teams eligible for
it, even if it was marked as "Is general". To edit the eligibility of teams for
any break round go to the **Breaks** item in the left-hand menu for a particular
tournament and then click **Team Eligiblity**.

Here you can select "all" or "none" to toggle all team eligiblities or edit them
using the tick boxes. Once you **save** it should return you to the main break
page which will display the number of teams marked eligible.

.. note:: Adjudicators can be marked as "breaking" on the **Feedback** page;
  clicking **Adjudicators** on the breaks page will take you straight there.

Generating the break
====================

Unlike team or speaker standings, each category's break (and the break ranks of
teams) are not determined automatically and updated continuously. Instead each
can be generated (and regenerated) as desired.

To do so go to the **Breaks** item in the left-hand menu and then click the
white button that corresponds to the break category you'd like to determine the
rankings for. When prompted, select **Generate the break for all categories** to
display the list of breaking teams.

From this page you can update the breaking teams list for this break category
(or all categories) as well as view and edit 'remarks' that account for cases in
which a team may not break (such as being capped or losing a coin toss).

.. caution:: Please double-check the generated break before announcing or
  releasing it. Although the break generation code is designed to handle edge
  cases, we don't test the code for such cases.

Creating draws for break rounds
===============================

Creating a draw for a break round proceeds as normal, except that the team
availability process is skipped. Instead, when you visit the availability page
for that round it will have automatically determined which teams should be
debating based upon the determined break for that category. Once a draw has been
generated it will then use the relevant break ranks to create the matchups (ie
1st-breaking vs 16th-breaking, 2nd vs 15th, *etc.*). Subsequent break rounds
will then also automatically determine matchups based on the previous round's
results and room ranks.

If the "break size" of a break category is not a power of 2, it will treat the
first break round as a partial-elimination draw and only create a draw for the
teams not skipping the partial-elimination round. Subsequent break rounds will
then process as described above.
