=====================
Sending Notifications
=====================

Tabbycat offers integrations with email delivery services to send notifications to participants on certain enumerated events. Before you can use them, you will need to configure your app to use an external email provider, such as SendGrid, Mailgun or MailChimp.

.. _configuring-email-provider:

Configuring an email provider
=============================

  *Changed in version 2.6:* Tabbycat no longer automatically provisions SendGrid via Heroku.

Tabbycat does not come with an email provider. You will need to configure your app to use a third-party email provider. Your Tabbycat site will not be able to send emails until you have done this. There are a number of options for this. The right one for you will depend on your tournament size and budget.

.. _configuring-sendgrid:

SendGrid
--------

To use `SendGrid <https://sendgrid.com/>`_, you'll need to create your own (personal or business) SendGrid account. The free tier is unlikely to suffice. If you're a student, you may be eligible for `SendGrid's (free) offer <https://sendgrid.com/partners/github-education/>`_ under the `GitHub Education Pack <https://education.github.com/pack>`_.

Once you have a SendGrid account:

1. `Create an API key <https://app.sendgrid.com/settings/api_keys>`_ in your SendGrid account.

  There are `instructions for how to do this in the SendGrid documentation <https://sendgrid.com/docs/User_Guide/Settings/api_keys.html>`_. The only permission that is needed is the "Mail Send" permission, so you can turn off all others if you want to be safe.

2. Set the following config vars in Heroku Dashboard (or using the Heroku CLI, if you have it):

  - Set ``SENDGRID_API_KEY`` to your API key, which will start with ``SG.*******``.
  - Set ``DEFAULT_FROM_EMAIL`` to the email address you want your emails to appears as coming from. This will probably need to be an email address that you can verify ownership of to SendGrid (see next step).

3. You'll probably need to complete sender authentication on SendGrid by following `these instructions in the SendGrid documentation <https://sendgrid.com/docs/for-developers/sending-email/sender-identity/>`_. Specifically, if sending a test email raises an error about "not matching a verified Sender Identity" (this is likely), you need to complete one of the two methods listed there:

  - *Single Sender Verification*, if you're comfortable with all of Tabbycat's emails coming from an email address that belongs to you and exists (*e.g.* your personal email address). This is more likely to be convenient for most users.
  - *Domain Authentication*, if you have access to a domain whose DNS record you control, *e.g.* a tournament or society website hosted on its own domain.

4. Send a test email using the tool on your Tabbycat site's home page.

  *Changed in version 2.6:* The ``SENDGRID_USERNAME`` and ``SENDGRID_PASSWORD`` config vars are deprecated in favour of ``SENDGRID_API_KEY``.

.. admonition:: Upgrading from legacy settings
  :class: tip

  If you've recently upgraded to version 2.6, and need to update your config vars, follow these instructions. First, check if the value of the config var ``SENDGRID_USERNAME`` is ``apikey``. If it is, you can do the following:

  1. Create a new config var ``SENDGRID_API_KEY``, and copy the value from ``SENDGRID_PASSWORD`` to it. This value should start with ``SG.******``. Be sure you have the value saved (try sending a test email now) before you continue.
  2. Delete the config vars ``SENDGRID_USERNAME`` and ``SENDGRID_PASSWORD`` (whose value you just copied over).
  3. If it's not already set, set ``DEFAULT_FROM_EMAIL`` to the email address you want your emails to appears as coming from.

  If the value of ``SENDGRID_USERNAME`` is anything other than ``apikey``, you'll need to convert your SendGrid configuration to use an API key instead. To do so, follow the instructions under :ref:`configuring-sendgrid` above. Then, delete the old ``SENDGRID_USERNAME`` and ``SENDGRID_PASSWORD`` config vars.

Other email providers
---------------------

If you configure these config vars, Tabbycat will use them to send emails.

- ``DEFAULT_FROM_EMAIL``: Email to send from
- ``EMAIL_HOST``: Host server
- ``EMAIL_HOST_USER``: Username for authentification to host
- ``EMAIL_HOST_PASSWORD``: Password with username
- ``EMAIL_PORT`` (default ``587``): Port for server
- ``EMAIL_USE_TLS`` (default ``true``): Whether to use `Transport Layer Security <https://en.wikipedia.org/wiki/Transport_Layer_Security>`_ (``true`` or ``false``)

Events
======

Tabbycat includes a number of templated notifications that can be sent in various times. Variables which are included between curly brackets which are substituted for personalized information passed by email. Links to email will redirect to a page where the message can be changed and the participants selected.

All emails have the ``{{ USER }}`` and ``{{ TOURN }}`` variables to indicate who the email is sent to, and the tournament it relates to. The "From" in the emails will also be the tournament's name.

.. list-table::
  :header-rows: 1

  * - Email content and description
    - Variables

  * - **Adjudicator draw notification**

      Email to adjudicators indicating their room assignment.

      Available through the admin draw page.
    - * ``{{ ROUND }}``: The round name
      * ``{{ VENUE }}``: The venue of the assigned debate
      * ``{{ PANEL }}``: A list of all the adjudicators assigned to the venue (with positions)
      * ``{{ DRAW }}``: A list of the team matchup with their roles
      * ``{{ POSITION }}``: The target adjudicator's position in the panel
      * ``{{ URL }}``: A link to the adjudicator's private URL page

  * - **Team draw notification**

      Email to teams indicating their pairing.

      Available through the admin draw page.
    - * ``{{ ROUND }}``: The round name
      * ``{{ VENUE }}``: The venue of the assigned debate
      * ``{{ PANEL }}``: A list of all the adjudicators assigned to the venue (with positions)
      * ``{{ DRAW }}``: A list of the team matchup with their roles
      * ``{{ TEAM }}``: The team's code or short name
      * ``{{ SIDE }}``: The team's side

  * - **Private URL distribution**

      Email to participants giving them their private URL for electronic forms.

      Available through the private URLs page.
    - * ``{{ URL }}``: The personalized URL
      * ``{{ KEY }}``: The private code in the URL

  * - **Ballot submission receipt**

      Email to adjudicators of their ballot after tabroom confirmation.

      Sent automatically when their ballot's result status becomes confirmed,
      if enabled in the "Notifications" section of the tournament options.
    - * ``{{ DEBATE }}``: The name (with round & venue) of the relevent debate
      * ``{{ SCORES }}``: The submitted ballot with speaker scores and team names

  * - **Current team standings**

      Email to speakers with their point total.

      Available through the "Confirm Round Completion" page.
    - * ``{{ URL }}``: The URL of the team standings page (if public)
      * ``{{ TEAM }}``: The team's name
      * ``{{ POINTS }}``: The team's number of points

  * - **Motion release**

      Email to speakers with the motion(s) of the current round.

      Available through the admin draw page.
    - * ``{{ ROUND }}``: The name of the round
      * ``{{ MOTIONS }}``: A list of the motions released

  * - **Team information**

      Email to speakers with information pertaining to their team, such as eligibility and codes.

      Available through the Participants page.
    - * ``{{ SHORT }}``: The team's short name
      * ``{{ LONG }}``: The team's long name
      * ``{{ CODE }}``: The team's code name
      * ``{{ EMOJI }}``: The team's assigned emoji
      * ``{{ BREAK }}``: Break categories which the team is a member
      * ``{{ SPEAKERS }}``: A list of the speakers in the team
      * ``{{ INSTITUTION }}``: The team's affiliation

Event Webhook
=============

With SendGrid, the status of sent emails can be sent to Tabbycat to be displayed, giving an indication of failures and whether participants have opened the messages. To activate this feature, setup must be done both in your SendGrid account and in Tabbycat.

1. Set a secret key in the Email section of the tournament's preferences. This key must be alphanumeric without any spaces.
2. Copy the "web-hook" link presented in a box at the top of the "email participants" page.
3. Go to https://app.sendgrid.com/settings/mail_settings and select "Event Notifications"
4. Enable the feature and paste the Tabbycat URL under "HTTP POST URL".
5. Select the notifications to keep track (or all of them).

.. caution:: Each email and change in status sent to Tabbycat will add a row to the database. If the number of rows is limited, as is for free Heroku apps, enabling the webhook may use up a significant number of rows. Be selective in the events to keep track.
