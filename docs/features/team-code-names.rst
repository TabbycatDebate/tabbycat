.. _team-code-names:

===============
Team Code Names
===============

Some tournaments use "code names" to obscure the institutional affiliations of
teams. For example, rather than calling a team "Harvard DK", they would be
presented in the draw as "Butterfly". A natural way to do this would be just
to change the name of every team, but then the team's "real name" would be
hidden from tournament staff, too.

Instead, Tabbycat allows you to assign code names to teams, alongside their real
names. This way, you can have code names show to participants, while real team
names show in administrative views (*e.g.* allocating adjudicators). It also
allows you to "decode" team names for elimination rounds or final tab release
easily, without having to actually change every team's name.

.. warning:: While the most frequently-used public views have been checked to
    ensure that they show only code names, not all views have been checked
    thoroughly. Please check views using demonstration data on a test site,
    configured in the same way that you would use it at your tournament, before
    using code names at a real tournament.

Assigning code names
====================

Most methods of importing teams, including the simple importer and the
``importtournament`` command, automatically assign code names to teams.
The code name is the name of the emoji that is automatically assigned at the
same time. For example, the team assigned 🦋 will be code-named "Butterfly".

If you wish to use your own code names, you need to set the "code name" field
of each team. Here are two ways to do this:

- **Edit Database area:** Enter the Edit Database area, and under **Participants
  > Teams**, click **Change**. Modify each team one by one, entering a new code
  name then saving.
- ``importtournament`` **command:** If you imported a tournament from CSV files,
  you can just add a ``code_name`` column to your teams CSV file.

Displaying code names
=====================

Code names are disabled by default; to enable then, go to **Setup >
Configuration > Public Options**, and change the **Team code names** option.
You can choose between the following options:

- Do not use code names
- Use real names everywhere, and show code names in tooltips
- Use code names for public; real names with code names in tooltips for admins
- Use code names for public; code names with real names in tooltips for admins
- Use code names everywhere; do not use tooltips (real names show in some admin views)

"Code names in tooltips" means that the code name will display in the details
box that appears when you roll over a team's name, and similarly for real names.

One typical use is as follows:

- Before the tournament, set the team code names setting to *Use code names for
  public; real names with code names in tooltips for admins*. This hides real
  names from anything participants would see, but continues to refer to teams in
  administrative views by real names.
- After the break is announced, set it to *Use real names everywhere, and show
  code names in tooltips*. This basically decodes all team names, while still
  allowing people to look up the (now former) code name of a team.

.. tip:: If you're enabling team codes, you probably want to disable the
    **Show team institutions** option too.
