.. _user-accounts:

=============
User Accounts
=============

For obvious reasons, user logins are required to data entry and administrative functions. Conceptually, there are different levels of access:

.. list-table::
  :header-rows: 1
  :stub-columns: 1
  :widths: 15 25 45

  * - Access
    - Grants access to
    - Is capable of

  * - Public (no login)
    - Publicly available information
    - Viewing pages marked as public as permitted by the tournament

  * - Private URL (no login)
    - Individualised information and data entry
    - Submitting new ballots/feedback/checkins as permitted by the tournament

  * - Regular user
    - Administrator and assistant areas based on permissions
    - Manage tournaments to the extent permitted

  * - Super-user
    - The administrator and assistant areas for all tournaments
    - Manage any tournament

  * - Staff
    - The Edit Database area
    - Editing the database directly

If a user account on the tab system belongs to someone who is also a participant in the tournament (*e.g.*, a chief adjudicator), these two accesses are completely separate. User accounts are only used to regulate access to administrative functions. Tabbycat doesn't know about any relationship between user accounts, and who is participating in the tournament.

Account roles
=============

You should create individual accounts for each person who needs to access the tab system.

Tournament participants (other than tournament officials) do not need an account. Everything they need to know can be accessed without an account. If you're using electronic ballots or electronic feedback, they access these using a URL that only they know (see :ref:`private-urls`).

When doing data entry, users should use the **assistant area**. The administrator area is intended for managing the tournament, and should **not** in general be used for data entry. Specifically, the administrator area lacks checks that are important for data integrity assurance. It should be used only to override the normal :ref:`data entry <data-entry>` procedure, for example, to unconfirm or modify a ballot.

The **Edit Database** interface should not be used except where it is actually necessary. There are a few functions which require this, but as a principle, it shouldn't be used as a matter of course.

.. note:: In theory, you could grant an account staff status but not super-user status. But then they'd be allowed to edit the database, but not run the tournament, which would be weird.

User permissions
================

In addition to account roles, Tabbycat has a concept of per-tournament permissions, where users can be assigned to only have access to specific parts of the administrator side of specific tournaments. These permissions can also be combined into "groups" to give standardized accesses to many users at once, such as CAs. When creating a tournament, a few default groups are created. Note that the assistant areas will still be accessible, to the extent of the "Assistant user access" tournament setting.

Groups can only be created or modified through Edit Database, as well as assigning specific permissions to users. Users may be added to a group through the invitation feature described below.

Invite people to create accounts
================================

If you wish to invite a tournament official to create their own account and assign permissions, you can do so:

1. Go to the Configuration area of the tournament.
2. Select the **Invite User to Create an Account** action.
3. Enter the email of the person to invite, and their role in the tournament.
4. They will receive an email with a link for them to create an account. The link expires after 24 hours.

.. note:: It is not possible to create a link that automatically gives super-user or staff access. You should either manually create other super-users, or use the admin interface to promote them once they have created an account this way.

Creating accounts manually
==========================

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
