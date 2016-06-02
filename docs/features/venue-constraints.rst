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