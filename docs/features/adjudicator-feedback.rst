.. _adjudicator-feedback:

====================
Adjudicator Feedback
====================

You can set the questions that are used on adjudicator feedback forms. The only field that is permanently there is the ``score`` field, which is an overall score assessing the adjudicator. All other questions (including a generic comments section) must be defined if you want them to be on the form.

Currently, there are two methods of setting questions:

- Through the :ref:`edit database area <user-accounts>`. Go to **Setup** >
  **Edit Database**, then click **Change** next to *Adjudicator feedback
  questions*. You can add questions here.
- Using the :ref:`importtournament command <importtournament-command>`.

Most of what you need to know is explained in help text in the edit database area. (Even if you're using ``importtournament``, you might find the field
descriptions in the edit database area helpful.) Some more details are here.

Answer types and options
========================

+-----------------------+----------------------+---------------------------------------+
|          Type         |   Relevant options   |               Appearance              |
+=======================+======================+=======================================+
| **checkbox**          | \-                   | .. image:: images/checkbox.png        |
+-----------------------+----------------------+---------------------------------------+
| **yes/no (dropdown)** | \-                   | .. image:: images/yesnodropdown.png   |
+-----------------------+----------------------+---------------------------------------+
| **integer (textbox)** | min_value, max_value | .. image:: images/integer-textbox.png |
+-----------------------+----------------------+---------------------------------------+
| **integer scale**     | min_value, max_value | .. image:: images/integer-scale.png   |
+-----------------------+----------------------+---------------------------------------+
| **float**             | min_value, max_value | .. image:: images/float.png           |
+-----------------------+----------------------+---------------------------------------+
| **text**              | \-                   | .. image:: images/text.png            |
+-----------------------+----------------------+---------------------------------------+
| **long text**         | \-                   | .. image:: images/longtext.png        |
+-----------------------+----------------------+---------------------------------------+
| **select one**        | choices              | .. image:: images/select-one.png      |
+-----------------------+----------------------+---------------------------------------+
| **select multiple**   | choices              | .. image:: images/select-multiple.png |
+-----------------------+----------------------+---------------------------------------+

Options:

- **min_value** and **max_value** specify the minimum and maximum allowable values in the field. Mandatory for "integer scale" types and optional for "integer (textbox)" and "float" types.
- **choices** is used with "select one" and "select multiple" types, and is a ``//``-delimited list of possible answers, *e.g.* ``biased//clear//concise//rambly//attentive//inattentive``
- **required** specifies whether users must fill out the field before clicking "submit". This requirement is only enforced on public submission forms. It is not enforced on forms entered by tab room assistants.

  The exception to this is the "checkbox" type. For checkboxes, "required" means that the user cannot submit the form unless the box is checked. Think of it like an "I agree to the terms" checkbox. This isn't a deliberate design decision—it's just a quirk of how checkboxes work on web forms.

Want another answer type?
=========================

We don't really intend to add any further complexity to the built-in feedback
system. If the above answer types don't cover your needs, we suggest using a
third-party feedback system. You might be able to adapt `SurveyMonkey <http://www.surveymonkey.com/>`_, `Google Forms <https://www.google.com/forms/about/>`_
or `Qualtrics <http://qualtrics.com>`_ to your needs.

We may be persuaded to make an exception if the new question type you have in
mind is easy to add: that is, if it is straightforward to implement using
standard web page elements and fits into the existing questionnaire framework
(see :ref:`feedback-questionnaires` below). If you think there is such a case,
please contact us using the contact details in the :ref:`authors` section.

.. _feedback-questionnaires:

Different questionnaires
========================

Tabbycat allows you to specify two questionnaires: one for feedback submitted by
teams, and one for feedback submitted by adjudicators. You must specify in each
question whether to include the question in each questionnaire.

- **from_team**, if checked, includes the question in feedback submitted by
  teams
- **from_adj**, if checked, includes the question in feedback submitted by
  adjudicators

Who gives feedback on whom?
===========================
Tabbycat allows for three choices for which adjudicators give feedback on which
other adjudicators:

- Chairs give feedback on panellists and trainees
- Chairs give feedback on panellists and trainees, and panellists give feedback
  on chairs
- All adjudicators, including trainees, give feedback on all other adjudicators
  they have adjudicated with

You can set this in the **feedback paths** option under *Setup* >
*Configuration* > *Feedback*. Your choice affects each of the following:

- The options presented to adjudicators in the online feedback form
- The printable feedback forms
- The submissions expected when calculating feedback progress and highlighting
  missing feedback

The feedback paths option only affects feedback from adjudicators. Teams are
always assumed to give feedback on the orallist, and they are encouraged to do
so through hints on the online and printable feedback forms, but there is
nothing technically preventing them from submitting feedback from any
adjudicator on their panel.

.. admonition:: Advanced users
  :class: tip

  If you need a different setting, you need to edit the source code.
  Specifically, you should edit the function ``expected_feedback_targets`` in
  tabbycat/adjfeedback/utils.py.

  Unless we can be convinced that they are very common, we don't intend to add
  any further choices to the feedback paths option. If your needs are specific
  enough that you need to differ from the available settings, they are probably
  also beyond what is sensible for a built-in feedback system, and we recommend
  using a third-party feedback system instead.

How is an adjudicator's score determined?
=========================================

For the purpose of the automated allocation, an adjudicator's overall score is a
function of their base score, the current round's feedback weight, and their
average feedback score. This number is calculated according to the following
formula:

.. math::

  \textrm{score} = (1-w)\times\textrm{base score} + w\times\textrm{average feedback score}

where :math:`w` is the feedback weight for the round. Note that because the feedback score is averaged across all pieces of feedback (rather than on a per-round total) rounds in which a person receives feedback from many sources (say from all teams and all panellists) could impact their average score much more than a round in which they only receive feedback from one or two sources.

Under this formula, each round's feedback weight can be used to determine the
relative influence of the base score vs feedback in determining the overall
score. As an example, say that an adjudicator received 5.0 as their base score,
but their average feedback rating has thus far been 2.0. If the current rounds'
feedback weight is set to 0.75, then their overall score would be 2.75. If the
current round's feedback weight is set to 0.5 their score would be 3.5. If the
weight was 0, their score will always be their base score; if the weight was 1
it will always be their average feedback value.

.. note:: To change the weight of a round you will need to go to the Edit Database area, open the round in question, and change its *Feedback weight* value. It is common to set rounds with a low feedback weight value early on in the tournament (when feedback is scant) and to increase the feedback weight as the tournament progresses.

.. note:: A participant's base score can, in conjunction with feedback weight, also be used as a manual override for an adjudicator's overall ranking. At several tournaments, adjudication cores have set every round's feedback weight to 0, and manually adjusted an adjudicator's base score in response to feedback they have received and reviewed. In this way complete control over every adjudicator's overall score can be exerted.

.. note:: If feedback from trainee adjudicators is enabled, any scores that they submit in their feedback are not counted towards that adjudicator's overall score.

Ignoring/Discarding feedback
============================

There are some cases where feedback should be discarded or ignored, but there are some differences between the two. Discarded feedback is mostly due to having another piece of feedback that supersedes the discarded ones. Ignored feedback is different as it still counts the affected feedback as submitted, just inconsequential, ignored in the adjudicator's score calculation.

Feedback can be marked as discarded in the database view, under the ``confirmed`` field. It can also be marked as ignored in the same view. Controls to reverse these designations are also available there. To mark feedback as ignored, an option is available in the administrator's and assistant's feedback adding form, as well in the form of a toggle link at the bottom of each card.
