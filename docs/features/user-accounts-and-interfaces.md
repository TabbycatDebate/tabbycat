# User Accounts

For obvious reasons, user logins are required to data entry and administrative functions. There are (conceptually) four levels of access:

| Access    | Should be used by  | Grants access to | Is capable of |
| --------- | ------------------ | ---------------- | ------------- |
| Public    | The public         | Publicly available information. | Viewing things, and submitting new ballots/feedback if that function is enabled. |
| Assistant    | Data entry helpers | Specialised data entry (ballots and feedback). | Entering and confirming ballots and feedback. |
| Superuser | Adjudication core  | The Tabbycat admin interface. | Generating draws, editing ballots, feedback and adjudicator scores, checking in ballots and people.
| Staff     | Tab director       | The Tabbycat and Data Admin interfaces. | Editing the database directly. |

## Account Roles

If the adjudication core and tab directors will be helping with data entry, you should create a "assistant" account for them as well. These people will then have two accounts each: one with assistant access, which is used for data entry, and one with superuser access, which is used for everything else.

Specifically, the Tabbycat admin interface should **not**, in general, actually be used for data entry. That interface doesn't include some checks that are important for data integrity assurance. It should be used only to override the normal [data entry](data-entry.md) procedure, for example, to unconfirm a ballot or edit a score.

The Data Admin interface should certainly not be used except where it is actually necessary. There are a few functions which require this, but as a principle, it shouldn't be used as a matter of course.

## Adding Accounts

To add an account:

1. Go to *BASE_URL/admin/auth/user/* and click "Add user" in the top right.

2. Ask the user to enter a username and password.
   * Only they should know what the password is.
   * If you're hosting on the internet, all passwords should be at least moderately strong!
   * Passwords are stored as hashes, not as raw passwords, so it's (in theory, practically) impossible for you to figure out what their password is.

3. If they're being assigned assistant privileges, click "Save" or "Save and add another". If they're being assigned superuser and/or staff privileges, then click "Save and continue editing", and check the appropriate boxes before clicking "Save". If you also wanted their names to be associated with their accounts, click "Save and continue editing" and fill out the relevant fields. But their names *etc.* aren't used for anything by Tabbycat.