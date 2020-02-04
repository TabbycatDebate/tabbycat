.. _user-accounts:

=============
User Accounts
=============

For obvious reasons, user logins are required to data entry and administrative functions. Conceptually, there are four levels of access:

.. list-table::
  :header-rows: 1
  :stub-columns: 1
  :widths: 15 15 25 45

  * - Access
    - Should be used by
    - Grants access to
    - Is capable of

  * - Public
    - The public
    - Publicly available information.
    - Viewing things, and submitting new ballots/feedback if electronic submission is permitted by the tournament.

  * - Assistant
    - Data entry helpers
    - The assistant area
    - Entering, confirming and printing ballots and feedback, checking in ballots and people, and displaying the draw.

  * - Superuser
    - Chief adjudicators
    - The administrator and assistant areas
    - Generating draws, allocating adjudicators and venues, and editing ballots, feedback and adjudicator scores.

  * - Staff and superuser
    - Tab director
    - The administrator, assistant and Edit Database areas
    - Editing the database directly.

If a user account on the tab system belongs to someone who is also a participant in the tournament (*e.g.*, a chief adjudicator), these two capacities are completely separate. User accounts are only used to regulate access to administrative functions. Tabbycat doesn't know about any relationship between user accounts, and who is participating in the tournament.

Account roles
=============

You should create an account for each person who needs to access the tab system. When you create an account in the Edit Database area, there are checkboxes for **Superuser status** and **Staff access**. Superusers have access to the administrator area, and staff have access to the Edit Database area. You should grant permissions as follows:

- Tab directors should get both superuser and staff status.
- Chief adjudicators and their deputies should get superuser status, but not staff status.
- Tab assistants (helping only with data entry) should get neither superuser nor staff status.

Tournament participants (other than tab staff) do not need an account. Everything they need to know can be accessed without an account. If you're using electronic ballots or electronic feedback, they access these using a URL that only they know (see :ref:`private-urls`).

When doing data entry, users with superuser status should use the **assistant area**. The administrator area is intended for managing the tournament, and should **not** in general be used for data entry. Specifically, the administrator area lacks checks that are important for data integrity assurance. It should be used only to override the normal :ref:`data entry <data-entry>` procedure, for example, to unconfirm or modify a ballot.

The **Edit Database** interface should not be used except where it is actually necessary. There are a few functions which require this, but as a principle, it shouldn't be used as a matter of course.

.. note:: In theory, you could grant an account staff status but not superuser status. But then they'd be allowed to edit the database, but not run the tournament, which would be weird.

Adding accounts
===============

To add an account:

1. Go to the Edit Database area of the site.

2. Under **Authentication and Authorization**, click the **Add** link next to **Users**.

3. Ask the user to enter a username, password and possibly email address.

   - Only they should know what the password is.
   - If you're hosting on the internet, all passwords should be at least moderately strong!
   - Passwords are not stored as raw passwords, so you can't figure out what their password is.
   - The email address is optional.
   - This email address is only used to reset their password if they forget it, and has nothing to do with the email address that Tabbycat uses to send emails to tournament participants (*e.g.* private URL links).

4. If they are being assigned superuser and/or staff status, check the relevant boxes.

5. Click "Save" or "Save and add another".
