.. _standings-rules:

===============
Standings Rules
===============

Team standings rules
====================

In Tabbycat, you can choose how teams are ranked in the team standings. For
example, at Australs, teams are ranked first on the number of wins, and second
on their total speaker score. The setting that specifies how teams are ranked is
called the **team standings precedence**. The team standings precedence is used:

- When displaying the team tab,
- Whenever a power-paired draw is generated, and
- When computing which teams are in the break.

When you choose the team standings precedence, you choose from a list of
*metrics*. Then, in the standings, teams will be sorted first by the first
metric, then by the second metric, and so on. You must choose at least one
metric, and you can choose up to eight. Teams tied on all metrics will have the
same rank.

If you like, you can also choose **team standings extra metrics**, which are
metrics that will be shown in the team standings, but not used to rank teams.

.. list-table::
  :header-rows: 1
  :stub-columns: 1
  :widths: 25 75

  * - Metric
    - Description

  * - Wins
    - How many debates the team has won.

  * - Points
    - How many points the team has. For two-team formats, this is just a synonym
      for wins, and differs only in column labelling. For BP, this is 3 points
      for a first, 2 for a second, 1 for a third and 0 for a fourth.

  * - Points (2/1/0)
    - How many points the team has, where teams earn 2 points for a win, 1 point
      for a loss and 0 points for a forfeit.

  * - Total speaker score
    - The sum of all speaker scores attained in all debates.

  * - Average speaker score
    - The average total speaker score over all debates the team has had, not
      counting debates where they or their opponents forfeited.

  * - Speaker score standard deviation
    - The standard deviation of total speaker scores over all debates the team
      has had, not counting debates where they or their opponents forfeited.
      This metric is ranked in ascending order (smaller standard deviations
      ranked higher).

  * - Sum of margins
    - The sum of all margins. Wins are positive, losses are negative.

  * - Average margin
    - The average margin over all debates the team has had, not counting debates
      where they or their opponents forfeited.

  * - Draw strength
    - The sum of the number of wins of every team this team has faced so far.

      This is also known in some circuits as *win points*, *opp wins* or *opp
      strength*.

  * - Votes/ballots carried
    - The number of adjudicators that gave this team a win across all of their
      debates. Also known as the number of *ballots* or *judges* a team has.

      In cases where the panel is smaller or larger than 3, this number is
      normalised to be out of 3. For example, if a panel of five splits 3--2,
      then the winning team is recorded as gaining 1.8 votes, and the losing
      team is recorded as gaining 1.2. This also means that solo adjudicators
      are always worth three votes.

  * - Number of firsts
    - The number of debates in which the team came first. Only makes sense for
      British Parliamentary.

  * - Number of seconds
    - The number of debates in which the team came second. Only makes sense for
      British Parliamentary.

  * - Who-beat-whom
    - If there are exactly two teams tied on all metrics earlier in the
      precedence than this one, then check if the teams have faced each other.
      If they have, the team that won their encounter is ranked higher. If they
      have seen each other more than once, the team that has won more of their
      encounters is ranked higher.

      If there are more than two teams tied, this metric is not applied.

      This metric can be specified multiple times. Each time who-beat-whom
      occurs, it applies to all the metrics earlier in the precedence than the
      occurrence in question.

  * - Who-beat-whom (in divisions)
    - As for who-beat-whom, but only compares for teams in the same division.
      That is, the metric applies whenever there are exactly two teams from the
      same division exactly tied.


Speaker standings rules
=======================

The speaker standings precedence is only used in speaker standings (*i.e.*, it
doesn't affect the operation of the tournament). As for team standings, the
**speaker standings precedence** specifies which metrics are used to rank
speakers, with the second metric tie-breaking the first, the third tie-breaking
the second, and so on. The **speaker standings extra metrics** are metrics
that will be shown in the speaker standings, but won't be used to rank speakers.

.. list-table::
  :header-rows: 1
  :stub-columns: 1
  :widths: 25 75

  * - Metric
    - Description

  * - Total
    - The sum of all speaker scores attained by the speaker. Note that if a
      speaker misses a round, they'll typically be relegated to the bottom of
      the speaker standings by this metric.

  * - Average
    - The average of all speaker scores attained by the speaker.

  * - Trimmed mean
    - The average speaker score after excluding their highest and lowest speaker
      scores. Also known as the *high-low drop*, *truncated mean* or *Olympic
      average*.

      If the speaker has only one or two scores, this metric just returns the
      average of those scores, without excluding any.

  * - Standard deviation
    - The standard deviation of all speaker scores attained by the speaker.
      This metric is ranked in ascending order (smaller standard deviations
      ranked higher).

  * - Average speaker score
    - The average total speaker score over all debates the team has had, not
      counting debates where they or their opponents forfeited.

  * - Number of speeches given
    - The number of speaker scores associated with the speaker. (In tournaments
      where teams can rotate speakers, this may not be all rounds.) This metric
      is normally used as an "extra" (unranked) metric, because it'd be weird
      to rank by number of speeches given, but you can if you want to.


Motion balance
==============

The motion balance page applies a statistical test to estimate the degree to which a motion is imbalanced. This is calculated by first making an underlying assumption that a motion is generally fair. This will be our null hypothesis: that, for a given motion, affirmative teams won the same number of times as negative teams.

Our chi-squared test will then be centred around disproving this hypothesis. If we disprove the hypothesis, we say that, in the context of this tournament and this draw, the motion ended up being unbalanced. However (technically speaking) if we fail to reject the null hypothesis, we would conclude that there is insufficient evidence to suggest that the motion was unbalanced in the context of this tournament.

The test proceeds by `calculating the chi-squared stat, then running a series of tests <https://github.com/TabbycatDebate/tabbycat/blob/develop/tabbycat/motions/statistics.py#L98>`_. The tests are where we go a little off-book with respect to statistical methodology. Normally we would test at a single "level of significance" (ie. with a certain degree of certainty), but that's insufficient in telling us how bad a motion ended up being. So, instead, we conduct a range of tests with a range of levels of significance, and calculate the minimum level of significance that causes our null hypothesis to be rejected. Using the minimum level of significance that rejects our null hypothesis, we can then grade the fairness of the motion on a scale. Motions whose tests fall below a certain threshold will be considered fair, while others will be graded based on the minimum.

For formats with topic selection, the same test is applied using the number of affirmative and negative vetoes in place of wins. The assumption here is that, during the time allotted for motion selection, teams estimate how appealing a motion is from their position, and then veto the topic that they feel is least favourable. Thus, the null hypothesis is that a motion that is perceived of as fair would be vetoed by affirmative and negative teams to an equal degree.
