# Adjudicator Feedback

You can set the questions that are used on adjudicator feedback forms. The only field that is permanently there is the `score` field, which is an overall score assessing the adjudicator. All other questions (including a generic comments section) must be defined if you want them to be on the form.

The only current method of setting questions is through the [[Django admin interface|User accounts and interfaces]]. Go to the Django admin interface, then click **Change** next to *Adjudicator feedback questions*. You can add questions here.

Most of what you need to know is explained in help text on that page. Some more details are here.

## Answer types

| Type | Relevant options | Appearance |
|------|------------------|------------|
| **checkbox** |  - | ![](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/answer-types/checkbox.png)
| **yes/no (dropdown)** | - | ![](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/answer-types/yesnodropdown.png)
| **integer (textbox)** | min_value, max_value | ![](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/answer-types/integer-textbox.png)
| **integer scale** | min_value, max_value | ![](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/answer-types/integer-scale.png)
| **float** | min_value, max_value | ![](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/answer-types/float.png)
| **text** |  - | ![](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/answer-types/text.png)
| **long text** |  - | ![](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/answer-types/longtext.png)
| **select one** | choices | ![](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/answer-types/select-one.png)
| **select multiple** | choices | ![](https://raw.githubusercontent.com/wiki/czlee/tabbycat/images/answer-types/select-multiple.png)

### Options

- **min_value** and **max_value** specify the minimum and maximum allowable values in the field. Mandatory for "integer scale" types and optional for "integer (textbox)" and "float" types.
- **choices** is used with "select one" and "select multiple" types, and is a `//`-delimited list of possible answers, *e.g.* `biased//clear//concise//rambly//attentive//inattentive`
- **required** specifies whether users must fill out the field before clicking "submit". This requirement is only enforced on public submission forms. It is not enforced on forms entered by tab room assistants.
    - The exception to this is the "checkbox" type. For checkboxes, "required" means that the user cannot submit the form unless the box is checked. Think of it like an "I agree to the terms" checkbox. This isn't a deliberate design decision&mdash;it's just a quirk of how checkboxes work on web forms.

### Want for another answer type?

If the above answer types don't cover your needs, please [contact us](https://github.com/czlee/tabbycat#licensing-development-and-contact). If it's easy enough to add your requested type and if give us enough notice, we'll gladly add it for you. We should warn you though: we don't intend to develop Tabbycat feedback into a fully-fledged [SurveyMonkey](http://www.surveymonkey.com/) or [Google Forms](https://www.google.com/forms/about/)-style system. If your request amounts to this, we suggest using a third-party system.

As a guide, a type is "easy enough to add" if you can imagine easily how to implement it using standard web page elements, and it requires only basic structure encompassing only a single question.

## Different questionnaires

Tabbycat allows you to specify two questionnaires: team-on-orallist, and adjudicator-on-adjudicator. You must specify in each question whether to include the question in each questionnaire.

- **team on orallist**, if checked, includes the question on all team-on-orallist forms.
- **chair on panellist**, if checked, includes the question on *all* adjudicator-on-adjudicator forms.

> *The **panellist on panellist** and **panellist on chair** don't currently do anything, and **chair on panellist** is a misnomer, it actually means **adjudicator on adjudicator**. These are all there for future support.*