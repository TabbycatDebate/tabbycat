.. _adjudicator-feedback:

====================
Adjudicator Feedback
====================

You can set the questions that are used on adjudicator feedback forms. The only field that is permanently there is the ``score`` field, which is an overall score assessing the adjudicator. All other questions (including a generic comments section) must be defined if you want them to be on the form.

The only current method of setting questions is through the :ref:`edit database interface <user-accounts>`. Go to the **Edit Database**, then click **Change** next to *Adjudicator feedback questions*. You can add questions here.

Most of what you need to know is explained in help text on that page. Some more details are here.

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

If the above answer types don't cover your needs, please contact us using the contact details in the :ref:`authors` section. If it's easy enough to add your requested type and if you give us enough notice, we'll gladly add it for you. We should warn you though: we don't intend to develop Tabbycat feedback into a fully-fledged `SurveyMonkey <http://www.surveymonkey.com/>`_ or `Google Forms <https://www.google.com/forms/about/>`_-style system. If your request amounts to this, we suggest using a third-party system.

As a guide, a type is "easy enough to add" if you can imagine easily how to implement it using standard web page elements, and it requires only basic structure encompassing only a single question.

Different questionnaires
========================

Tabbycat allows you to specify two questionnaires: team-on-orallist, and adjudicator-on-adjudicator. You must specify in each question whether to include the question in each questionnaire.

- **team on orallist**, if checked, includes the question on all team-on-orallist forms.
- **chair on panellist**, if checked, includes the question on *all* adjudicator-on-adjudicator forms.

.. note:: The **panellist on panellist** and **panellist on chair** don't currently do anything, and **chair on panellist** is a misnomer, it actually means **adjudicator on adjudicator**. These are all there for future support.

How is an adjudicator's score determined?
=========================================

For the purpose of the automated allocation, an adjudicator's overall score is a function of their test score, the current round's feedback weight, and their average feedback score. This number is calculated as equal to:

``Test Score x (1 - Current Round's Feedback Weight) + (Current Round's Feedback Weight * Average Feedback Score)``

Under this formula, each round's feedback weight can be used to determine the relative influence of the test score vs  feedback in determining the overall score. As an example, say that an adjudicator received 5.0 as their test score, but their average feedback rating has thus far been 2.0. If the current rounds' feedback weight is set to 0.75, then their overall score would be 2.75. If the current round's feedback weight is set to 0.5 their score would be 3.5. If the weight was 0, their score will always be their test score; if the weight was 1 it will always be their average feedback value.

It is common to set rounds with a low feedback weight value early on in the tournament (when feedback is scant) and to increase the feedback weight as the tournament progresses.

.. note:: A participant's test score can, in conjunction with feedback weight, also be used as a manual override for an adjudicator's overall ranking. At several tournaments, adjudication cores have set every round's feedback weight to 0, and manually adjusted an adjudicator's test score in response to feedback they have received and reviewed. In this way complete control over every adjudicator's overall score can be exerted.
