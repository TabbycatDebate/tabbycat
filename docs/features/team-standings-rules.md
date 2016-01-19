# Team Standings Rules

There are currently two sets of rules implemented for ordering teams. You choose which one on the tournament configuration page, using the *Team standings rule* setting. There are two allowed values: `australs` and `nz`. If you use any other values, Tabbycat will crash.

There are plans to make this more configurable than it is currently. If you need any other standings rules, please [contact Chuan-Zheng to get them added](https://github.com/czlee/tabbycat#licensing-development-and-contact contact details here).

See also: [draw generation](draw-generation.md)

## Australs Rules

Use Australs rules by using `australs` in the *Team standings rule* configuration setting.

Australs rules rank teams first by number of wins, then by total speaker score. Teams that are equal on both wins and speaker score are ordered randomly when generating a draw, but will just show as the same rank on the team standings page.

## New Zealand Rules

Use New Zealand rules by using `nz` in the *Team standings rule* configuration setting.

New Zealand rules rank teams using the following priority:

1. Number of wins
1. Who-beat-whom, if exactly two teams are equal
1. Total speaker score
1. Who-beat-whom, if exactly two teams are equal
1. Draw strength
1. Who-beat-whom, if exactly two teams are equal

Teams that are equal after all of the above are ordered randomly when generating a draw, but will just show as the same rank on the team standings page.

The *who-beat-whom* rule applies whenever there are exactly two teams left to sort, for example, if there are only two teams in a wins bracket, or if there are exactly two teams that have the same number of wins and total speaker score. In this case, rather than sorting according to the normal key, we first check for any debates between those two teams, and rank the team who has won more of them first. If this doesn't help, then we resume with the next key to sort by.

Who-beat-whom does not apply when there are three or more teams that are otherwise equal.

> *__Technical note:__ Whenever who-beat-whom is invoked, a message is printed to the logs, which'll look something like this*:

    2014-08-17T23:57:43.074923+00:00 app[web.1]: who beat whom, Yale 2 vs Cornell 1: None wins against None

*Draw strength*, also known as *win points*, *opp wins* and *opp strength*, is the sum of the number of wins of every team that the team has faced so far.