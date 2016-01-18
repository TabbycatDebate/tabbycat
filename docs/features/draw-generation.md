# Generating a Draw

The draw generator is quite flexible. You can specify a number of settings to suit different tournaments' rules. See also: [Team standings rules](team-standings-rules.md)

## Draw Options

The options discussed here are set in the __Config__ page as described in [starting a tournament](../use/starting-a-tournament.md)

> *__Caution:__ These settings are not checked for validity when you save them. If you use an invalid string, Tabbycat will just crash when you try to generate the draw. This won't corrupt the database, but it might be momentarily frustrating.

| Option | Description | Allowable values |
|--------|--------|--------|
| __Draw odd brackets__ | How to resolve odd brackets | `pullup_top`<br />`pullup_bottom`<br>`pullup_random` <br><br> If sides are `random` or `balance`:<br />`intermediate`<br />`intermediate_bubble_up_down` <br><br> If sides are `allocated`:<br />`intermediate1`<br />`intermediate2`|
| __Draw side allocations__ | How to allocate aff/neg | `random`<br />`balance`<br />
| __Draw pairing method__ |  How to pair teams within brackets | `slide` <br /> `fold` <br> `random` |
| __Draw avoid conflicts__ |  How to avoid history/institution conflicts | `off`<br />`one_up_one_down`|

## Odd Bracket Resolution

The __draw odd brackets__ option specifies what you do when a bracket has an odd number of teams. (Obviously you have to do something, otherwise you can't pair off teams within the bracket.) There are two groups of methods: pull-up and intermediate bubbles.

- __Pull-up methods__ take one or more teams from the next bracket down, and move them into the odd bracket to fill the bracket.
- __Intermediate bubbles__ take the excess teams from the odd bracket and move them down into a new bubble, which sits between the odd bracket and the next one down (hence the name "intermediate"). It then takes one or more teams from the next bracket down and moves them to fill the new intermediate bubble.

The exact mechanics depend on how sides are allocated.  Sides are "pre-allocated" if the __draw side allocations__ setting is set to `allocated`, and aren't if it's anything else.

1. __When sides are not pre-allocated__

    - __Pull-up methods__ take a team from the next bracket down, and add them to the odd bracket to form an even bracket. You might pull up the top team from the next bracket, or the bottom team, or a randomly chosen team. These are specified with the strings `pullup_top`, `pullup_bottom` and `pullup_random` respectively.
    - __Intermediate bubbles__ take the bottom team from the odd bracket and match them against the top team from the next bracket. An intermediate bubble always has two teams. The string `intermediate` specifies this method.

    If you're using conflict avoidance and intermediate bubbles, you will probably want to use `intermediate_bubble_up_down` instead. This uses the "bubble-up-bubble-down" rule to swap teams out of an intermediate bubble if there is a history or institution conflict. This is defined in the Australs constitution and is analogous to the "one-up-one-down" rule.

    > *__Caution:__ Using `intermediate` with `one_up_one_down` does __not__ imply `intermediate_bubble_up_down`. You must enable `intermediate_bubble_up_down` specifically.*

2. __When sides are pre-allocated__

    When sides are pre-allocated, an "odd bracket" is one that has an uneven number of affirmative and negative teams. (So odd brackets can have an even number of teams, ''e.g.'' 4 affs and 2 negs.)

    - __Pull-up methods__ take as many teams from the next bracket down as necessary to fill the bracket. If there aren't enough teams in the next bracket down, it will take teams from the bracket after that, and so on, until the (original) odd bracket is filled. Higher brackets are always filled first. You might pull up the top teams from the next bracket, the bottom teams, or a random selection of teams. These are specified with the strings `pullup_top`, `pullup_bottom` and `pullup_random` respectively.
    - __Intermediate bubbles__ take the unpaired teams in a bracket, and move them down to a new intermediate bubble. It then takes the number of teams necessary from the opposite side, from the next bracket down, to fill the next bubble.

    `intermediate1` and `intermediate2` differ only in what happens if there aren't enough teams in the next bracket to fill the intermediate bubble. In `intermediate1`, it will just take teams from the bracket after that, and so on, until the intermediate bubble is filled. In `intermediate2`, it will split the intermediate bubble: the teams that can be paired with the next bracket form the first intermediate bubble, and then the teams that aren't form a new (unfilled) intermediate bubble, to be filled from teams from the bubble after that. This keeps going, splitting into as many intermediate bubbles as necessary, until all excess teams from the original odd bracket are paired.

## Side Allocations

There are four methods:

- `random` allocates randomly. Some tournaments might like this, but most will probably want to use `balance`, because `random` doesn't guarantee that a team won't be (say) affirming the entire tournament.
- `balance` assigns the team that has affirmed less so far the affirmative side (and, therefore, the team that has negated less the negative side). If both teams have affirmed the same number of times, it assigns sides randomly.
- `preallocated` is used for pre-allocated sides. If used, you must enter data for pre-allocated sides into the database, as specified below.
- `manual-ballot` is used for tournaments where the sides of the teams involved are not assigned in advance, but are instead determined by the teams themselves


__Pre-Allocated sides__

There isn't currently any way to edit side allocations from the front end. To do so from the back end, you need to create one `TeamPositionAllocation` entry for each team in each round. All teams must have an allocation for every round. There are a few ways to do this, take your pick:

- If you're using the `import_tournament` command, it reads sides from the file sides.csv.
- You can do this from the Data Admin interface, by going to the relevant team and adding a __team position allocation__ entry. That is:
- Click __Admin__ on the bottom right of any page after logging into an account with [User accounts and interfaces#superuser-access](user-accounts-and-interfaces.md).
- Next to __Teams__, click __Change__.
- Click on the name of the team you want to edit side allocations for.
- Add or edit the entry or entries in the __Team position allocations__ table at the bottom.
-You can also do this by writing a script that creates `TeamPositionAllocation` objects and saves them. Have a look at data/utils/add_random_side_allocations.py for an example.

## Pairing

It's easiest to describe these by example, using a ten-team bracket:

- `fold`: 1 vs 10, 2 vs 9, 3 vs 8, 4 vs 7, 5 vs 6.
- `slide`: 1 vs 6, 2 vs 7, 3 vs 8, 4 vs 9, 5 vs 10.
- `random`: paired at random within bracket.

Teams are always paired within their brackets, after resolving odd brackets.

## Conflict Avoidance

A __conflict__ is when two teams would face each other that have seen each other before, or are from the same institutions. Some tournaments have a preference against allowing this if it's avoidable within certain limits. The __draw avoid conflicts__ option allows you to specify how.

You can turn this off by using `off`. Other than this, there is currently one conflict avoidance method implemented.

The one-up-one-down method, specified with `one_up_one_down`, is the method specified in the Australs constitution. Broadly speaking, if there is a debate with a conflict:

- It tries to swap teams with the debate "one up" from it in the draw.
- If that doesn't work, it tries to swap teams with the debate "one down" from it in the draw.
- If neither of those works, it accepts the original conflicted debate.

It's a bit more complicated than that, for two reasons:

- History conflicts are prioritised over (''i.e.'', "worse than") institution conflicts. So it's fine to resolve a history conflict by creating an institution conflict, but not the vice versa.
- Each swap obviously affects the debates around it, so it's not legal to have two adjacent swaps. (Otherwise, in theory, a team could "one down" all the way to the bottom of the draw!) So there is an optimization algorithm that finds the best combination of swaps, ''i.e.'' the one that minimises conflict, and if there are two profiles that have the same least conflict, then it chooses the one with fewer swaps.

## Known Tournaments Draw Options

The settings that should be used for some tournaments are as follows:

| __Australs__ Settings | |
|------------|------------|
| Odd brackets | `intermediate_bubble_up_down` or `pullup_top` |
| Side resolution | `balance` |
| Pairing method | `slide` |
| Avoid conflicts | `one_up_one_down` |

| __Joynt Scroll__ Settings | |
|------------|------------|
| Odd brackets | `intermediate1` or `intermediate2` |
| Side resolution | `preallocated` |
| Pairing method | `fold` |
| Avoid conflicts | `off` |

## Draw Problems

__What do I do if the draw looks wrong?__

We've never encountered this situation before, but if you look at a draft draw and notice there's something wrong&mdash;say, it pulled up the wrong team&mdash;the only resolution is to edit the database through the back-end.

You can do this before the first result is entered for any of the affected debates. There's no continued relationship between the draw and previous rounds' results, so it's safe to edit it. But it's an exceptionally bad idea to do this once any result for the round is entered (by which time the debates should be over anyway), because some data will be deleted, and not necessarily all the data that should be.

> *__Warning!__ You can wreak a ''lot'' of havoc by editing the database, if you get something wrong. When you do this, the system doesn't check that a team isn't in two debates in the same round or anything like that, so you won't get any warnings, but Tabbycat will break later, possibly spectacularly. So be really, ''really'', careful.*

To do this:

- Go to the Data Admin interface
- Next to ''Debates'', click __Change__.
- Edit the draw.
- To edit a debate:
    - Find the debate you want to switch, and click on its ID.
    - Edit the ''Debate teams''. Always make sure there is exactly one affirmative team and exactly one negative team. (It's fine if the database is in an "invalid" state momentarily, so long as no-one else is doing anything at the same time.)
- To add a debate:
    - Click __Add debate__ (in the top-right corner)
    - Fill out the fields. Fields marked with an asterisk are mandatory, fields not are optional.
    - Add two debate teams, one affirmative and one negative. (This isn't mandatory, but Tabbycat will break if you leave the database in a state where each debate doesn't have one affirmative and one negative team.)
    - If you like, add debate adjudicators&mdash;but you can still do this from the normal "Edit adjudicators" interface, provided you haven't entered any results.
-  To remove a debate:
    - Find the debate(s) you want to delete, and click the checkbox next to it (them).
    - Scroll to the bottom of the page, set the dropdown box to "Delete selected debates", and click Go.
    - Review the confirmation before proceeding.
- Once you've made *all* the necessary changes, go back to the draw page, check that the new draft draw looks as you expect, and confirm it.

## Technical Notes

*The information in this section should be read in conjunction with the source code documentation.*

The draw module is based around `DrawGenerator`, a factory function that returns a subclass of `BaseDrawGenerator`. `DrawGenerator` takes two mandatory arguments: `draw_type`, a string, and `teams`, a list of `Team`-like objects.

As a design principle, the draw module does not rely on internal knowledge of `models.py`. Rather, to enforce abstraction and to ease unit testing, it is written as a stand-alone module that could, in principle, be used by other applications. Therefore, it defines an interface and uses duck-typing to work with inputs.

`Team`-like objects are the main part of this interface. The draw module doesn't provide a base object for `Team`-like objects, nor does it expect them to be a Django model or be called `Team`. Rather, it merely expects `Team`-like objects to have certain attributes, depending on the options passed to `DrawGenerator`. For example, for power-paired draws, `Team`-like objects must have the `points` attribute. (For further details, refer to the source code.) Because `DrawGenerator` returns the same objects in some methods, `Team`-like objects must be hashable.

The `make_draw()` method returns a list of `Pairing` objects. The `Pairing` class is defined in the draw module. Its `teams` attribute (and all attributes derived from it) contain the same `Team`-like objects that were passed to `DrawGenerator`.