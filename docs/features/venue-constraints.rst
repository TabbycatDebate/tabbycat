.. _venue-constraints:

=================
Venue Constraints
=================

Tabbycat supports a basic form of venue constraints. A **venue constraint** is a
requirement that a particular **team, adjudicator, institution** or **division**
be assigned to a venue in a particular **venue group**.  Typical uses would
include:

- Meeting venue accessibility requirements of particular teams (*e.g.* step-free
  access)
- Placing adjudication core and tab team members close to the tab room
- Keeping all debates in a division in one location

Constraints apply to **venue groups**, not individual venues. That is, you
specify that (say) a team should be given a venue from a particular *list* of
venues. Of course, it's permissible for a venue group to have only one venue in
it.

The algorithm used to satisfy venue constraints is not guaranteed to be optimal.
In some rare cases, it may propose an allocation that fails some constraints,
even though some other allocation would have satisfied all (or more)
constraints. In almost all practical circumstances, however, it should work, and
save human effort (and time) in specially allocating rooms.

Adding venue constraints
========================
To add a venue constraint, go to the **Edit Data** section (under Setup), scroll
down to "Venues", and you will see four times of venue constraints:

- Adjudicator venue constraints
- Division venue constraints
- Institution venue constraints (apply to teams, not adjudicators)
- Team venue constraints

Click the type of constraint you're like to add, then click the **+ Add [type]
venue constraint** button in the top-right of the page.

For each constraint, you need to specify three things:

- The adjudicator, division, institution or team demanding the constraint
- A venue group
- A priority

The priority is only used to resolve conflicts between constraints. If none of
your constraints will ever conflict, then the priority is arbitrary.

Applying venue constraints
==========================

Venue constraints are applied automatically when the draw is generated. However,
at this point, only team, institution and division constraints can be accounted
for. Generating the draw doesn't generate an adjudicator allocation, so if there
are any adjudicator venue constraints, they won't be taken into account.

If after you allocate adjudicators, or at any other point (say, after adding a
new venue constraint), you would like to re-run the venue allocation algorithm,
you can do so under **Edit Venues** (while looking at the draw), then in the
screen where you can edit venues, click the **Auto Allocate** button.

If a venue constraint couldn't be met, a message will show in the
"conflicts/flags" column of the draw. A constraint might not be met for a
number of reasons:

- It could be that constraints of different parties (say, one team and one
  adjudicator) conflicted, so only one could be fulfilled.
- It could be that all available rooms in the relevant venue group were already
  taken by other, higher-priority constraints.
- It could just be one of those edge cases that's too hard for the naïve
  algorithm to handle.

Currently, Tabbycat doesn't tell you which of these happened, so if the venue
allocation fails to meet all your constraints, it's on you to figure out why. In
most scenarios, we imagine you'll have few enough constraints that this will be
obvious; for example, if the chief adjudicator is judging a team with
accessibility requirements, it might be obvious that the latter's constraint
took priority. We might in future add support for more useful guidance on
conflicting constraints, but we currently consider this to be of low priority.
