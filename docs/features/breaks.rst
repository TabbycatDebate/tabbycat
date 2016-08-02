=========================
Breaks and Break Rounds
=========================

Creating Break Categories
=========================

Each tournament may have a single or multiple break categories that group a particular series of out-rounds such as an "Open" or "ESL" break.

If you set the 'Number of teams in the open break' field when creating a tournament using the 'Create New Tournament' section of the website, an Open break category and the required number of break rounds will be generated automatically. If you create the tournament in the **Edit Database**, or via an importer you may need to manually add Break Categories and assign them to the relevant break rounds. At the moment new break rounds must be added through the **Edit Database** interface (available in the **Setup** section once in a tournament). Once there go to **Break Qualification** > **break categories** and click **Add break category**. The fields required for each category should be relatively self-explanatory.

Setting Break Eligibility
=========================

Once a break category has been created it will not have any teams eligible for it, even if it was marked as "Is general". To edit the eligibility of teams for any break round go to the **Breaks** item in the left-hand menu for a particular tournament and then click **Edit Eligiblity**.

Here you can select "all" or "none" to toggle all team eligiblities or edit them using the tick boxes. Once you **save** it should return you to the main break page which will display the number of teams marked eligible.

.. note:: Adjudicators can be marked as "breaking" on the **Feedback** page; clicking **Adjudicators** on the breaks page will take you straight there.

Determining a Break
===================

Unlike team or speaker standings, each category's break ranks are not determined automatically and updated continuously. Instead each can be calculated (and re-calculated) as desired.

To do so go to the **Breaks** item in the left-hand menu and then click the white button that corresponds to the break category you'd like to determine the rankings for. When prompted, select **Generate the break for all categories** to display the list of breaking teams.

From this page you can update the breaking teams list for this break category (or all categories) as well as view and edit 'remarks' that account for cases in which a team may not break (such as being capped or losing a coin toss).

Creating Draws for Break Rounds
===============================

Creating a draw for a break round proceeds as normal, except that the team checkin process is skipped. Instead, when you visit the checkins page for that round it will have automatically determined which teams should be debating based upon the determined break for that category. Once a draw has been generated it will then use the relevant break ranks to create the matchups (ie 1st-breaking vs 16th-breaking, 2nd vs 15th, etc). Subsequent break rounds will then also automatically determine matchups based on the previous round's results and the initial break ranks of each team.

If the 'break size' of a particular break category is not a power of 2, it will treat the first break round as a partial-elimination draw and only create a draw for the teams not skipping the partial-elimination round. Subsequent break rounds will then process as described above.
