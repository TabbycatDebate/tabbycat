=====================
Sending Notifications
=====================

Tabbycat offers integrations with email delivery services to send notifications to participants on certain enumerated events. For sending these emails, `SendGrid <https://sendgrid.com/>`_ is readily available as an add-on in Heroku. It may be necessary to install the `SendGrid add-on <https://elements.heroku.com/addons/sendgrid>`_ manually. Other integrations may also be used in its place by changing the relevant environment variables.

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
      * ``{{ URL }}`: A link to the adjudicator's private URL page

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
      * ``{{ SCORES }}``: The submitted ballot with speaker scores ands team names

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
      * ``{{ DIVISION }}``: The team's division if applicable
      * ``{{ BREAK }}``: Break categories which the team is a member
      * ``{{ SPEAKERS }}``: A list of the speakers in the team
      * ``{{ INSTITUTION }}``: The team's affiliation
