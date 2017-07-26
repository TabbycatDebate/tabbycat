.. _standings-rules:

===============
Standings Rules
===============

Team Standings Rules
====================

In Tabbycat, you can choose how teams are ranked in the team standings. For
example, at Australs, teams are ranked first on the number of wins, and second
on their total speaker score. The setting that specifies how teams are ranked is
called the *team standings precedence*. The team standings precedence is used:

- When displaying the team tab,
- Whenever a power-paired draw is generated, and
- When computing which teams are in the break.

When you choose the team standings precedence, you choose from a list of
*metrics*. Then, in the standings, teams will be sorted first by the first
metric, then by the second metric, and so on. You must choose at least one
metric, and you can choose up to eight. Teams tied on all metrics will have the
same rank.

+--------------------+---------------------------------------------------------+
|       Metric       |                       Description                       |
+====================+=========================================================+
| **Wins**           | How many debates the team has won.                      |
+--------------------+---------------------------------------------------------+
| **Points**         | How many points the team has. Currently, this is just a |
|                    | synonym for wins, and differs only in column labelling. |
+--------------------+---------------------------------------------------------+
| **Points (2/1/0)** | How many points the team has, where teams earn 2 points |
|                    | for a win, 1 point for a loss and 0 points for a        |
|                    | forfeit.                                                |
+--------------------+---------------------------------------------------------+
| **Total speaker    | The sum of all speaker scores attained in all debates.  |
| score**            |                                                         |
+--------------------+---------------------------------------------------------+
| **Average speaker  | The average total speaker score over all debates        |
| score**            | the team has had, not counting debates where they or    |
|                    | their opponents forfeited.                              |
+--------------------+---------------------------------------------------------+
| **Sum of margins** | The sum of all margins. Wins are positive, losses are   |
|                    | negative.                                               |
+--------------------+---------------------------------------------------------+
| **Average margin** | The average margin over all debates the team has had,   |
|                    | not counting debates where they or their opponents      |
|                    | forfeited.                                              |
+--------------------+---------------------------------------------------------+
| **Draw strength**  | The sum of the number of wins of every team this team   |
|                    | has faced so far.                                       |
|                    |                                                         |
|                    | This is also known in some circuits as *win points*,    |
|                    | *opp wins* or *opp strength*.                           |
+--------------------+---------------------------------------------------------+
| **Votes/ballots    | The number of adjudicators that gave this team a win    |
| carried**          | across all of their debates. Also known as the number   |
|                    | of *ballots* or *judges* a team has.                    |
|                    |                                                         |
|                    | In cases where the panel is smaller or larger than 3,   |
|                    | this number is normalised to be out of 3. For example,  |
|                    | if a panel of five splits 3--2, then the winning team   |
|                    | is recorded as gaining 1.8 votes, and the losing team   |
|                    | is recorded as gaining 1.2. This also means that solo   |
|                    | adjudicators are always worth three votes.              |
+--------------------+---------------------------------------------------------+
| **Who-beat-whom**  | If there are exactly two teams tied on all metrics      |
|                    | earlier in the precedence than this one, then check if  |
|                    | the teams have faced each other. If they have, the team |
|                    | that won their encounter is ranked higher. If they have |
|                    | seen each other more than once, the team that has won   |
|                    | more of their encounters is ranked higher.              |
|                    |                                                         |
|                    | If there are more than two teams tied, this metric is   |
|                    | not applied.                                            |
|                    |                                                         |
|                    | This metric can be specified multiple times. Each time  |
|                    | who-beat-whom occurs, it applies to all the metrics     |
|                    | earlier in the precedence than the occurrence in        |
|                    | question.                                               |
+--------------------+---------------------------------------------------------+
| **Who-beat-whom    | As for who-beat-whom, but only compares for teams in    |
| (in divisions)**   | the same division. That is, the metric applies whenever |
|                    | there are exactly two teams from the same division      |
|                    | exactly tied.                                           |
+--------------------+---------------------------------------------------------+

.. note:: Some debugging information is printed to the logs when some of these metrics are invoked.


Motions Standings Test
======================

The motions tab and motions standings page applies a statistical test to estimate the degree to which a motion is imbalanced. This is calculated by first making an underlying assumption that a motion is generally fair. This will be our null hypothesis: that, for a given motion, affirmative teams won the same number of times as negative teams.

Our chi-squared test will then be centred around disproving this hypothesis. If we disprove the hypothesis, we say that, in the context of this tournament and this draw, the motion ended up being unbalanced. However (technically speaking) if we fail to reject the null hypothesis, we would conclude that there is insufficient evidence to suggest that the motion was unbalanced in the context of this tournament.

The test proceeds by `calculating the chi-squared stat, then running a series of tests <https://github.com/czlee/tabbycat/blob/develop/tabbycat/standings/motions.py#L40>`_. The tests are where we go a little off-book with respect to statistical methodology. Normally we would test at a single "level of significance" (ie. with a certain degree of certainty), but that's insufficient in telling us how bad a motion ended up being. So, instead, we conduct a range of tests with a range of levels of significance, and calculate the minimum level of significance that causes our null hypothesis to be rejected. Using the minimum level of significance that rejects our null hypothesis, we can then grade the fairness of the motion on a scale. Motions whose tests fall below a certain threshold will be considered fair, while others will be graded based on the minimum.

For formats with topic selection, the same test is applied using the number of affirmative and negative vetoes in place of wins. The assumption here is that, during the time allotted for motion selection, teams estimate how appealing a motion is from their position, and then veto the topic that they feel is least favourable. Thus, the null hypothesis is that a motion that is perceived of as fair would be vetoed by affirmative and negative teams to an equal degree.
