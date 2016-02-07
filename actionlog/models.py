from django.db import models
from django.conf import settings


class ActionLogManager(models.Manager):
    def log(self, *args, **kwargs):
        obj = self.model(*args, **kwargs)
        obj.full_clean()
        obj.save()


class ActionLogEntry(models.Model):
    # These aren't generated automatically - all generations of these should
    # be done in views (not models).

    ACTION_TYPE_BALLOT_CHECKIN = 'ba.ckin'
    ACTION_TYPE_BALLOT_CREATE = 'ba.crea'
    ACTION_TYPE_BALLOT_CONFIRM = 'ba.conf'
    ACTION_TYPE_BALLOT_DISCARD = 'ba.disc'
    ACTION_TYPE_BALLOT_SUBMIT = 'ba.subm'
    ACTION_TYPE_BALLOT_EDIT = 'ba.edit'
    ACTION_TYPE_FEEDBACK_SUBMIT = 'fb.subm'
    ACTION_TYPE_FEEDBACK_SAVE = 'fb.save'
    ACTION_TYPE_TEST_SCORE_EDIT = 'ts.edit'
    ACTION_TYPE_DRAW_CREATE = 'dr.crea'
    ACTION_TYPE_DRAW_CONFIRM = 'dr.conf'
    ACTION_TYPE_ADJUDICATORS_SAVE = 'aa.save'
    ACTION_TYPE_VENUES_SAVE = 've.save'
    ACTION_TYPE_DRAW_RELEASE = 'dr.rele'
    ACTION_TYPE_DRAW_UNRELEASE = 'dr.unre'
    ACTION_TYPE_DIVISIONS_SAVE = 'dv.save'
    ACTION_TYPE_MOTION_EDIT = 'mo.edit'
    ACTION_TYPE_MOTIONS_RELEASE = 'mo.rele'
    ACTION_TYPE_MOTIONS_UNRELEASE = 'mo.unre'
    ACTION_TYPE_DEBATE_IMPORTANCE_EDIT = 'db.im.edit'
    ACTION_TYPE_ROUND_START_TIME_SET = 'rd.st.set'
    ACTION_TYPE_BREAK_ELIGIBILITY_EDIT = 'br.el.edit'
    ACTION_TYPE_BREAK_GENERATE_ALL = 'br.gene'
    ACTION_TYPE_BREAK_UPDATE_ALL = 'br.upda'
    ACTION_TYPE_BREAK_UPDATE_ONE = 'br.upd1'
    ACTION_TYPE_BREAK_EDIT_REMARKS = 'br.rm.edit'
    ACTION_TYPE_AVAIL_TEAMS_SAVE = 'av.tm.save'
    ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE = 'av.aj.save'
    ACTION_TYPE_AVAIL_VENUES_SAVE = 'av.ve.save'
    ACTION_TYPE_OPTIONS_EDIT = 'op.edit'

    ACTION_TYPE_CHOICES = (
        (ACTION_TYPE_BALLOT_DISCARD, 'Discarded ballot set'),
        (ACTION_TYPE_BALLOT_CHECKIN, 'Checked in ballot set'),
        (ACTION_TYPE_BALLOT_CREATE,
         'Created ballot set'),  # For tab assistants, not debaters
        (ACTION_TYPE_BALLOT_EDIT, 'Edited ballot set'),
        (ACTION_TYPE_BALLOT_CONFIRM, 'Confirmed ballot set'),
        (ACTION_TYPE_BALLOT_SUBMIT, 'Submitted ballot set from the public form'
         ),  # For debaters, not tab assistants
        (ACTION_TYPE_FEEDBACK_SUBMIT, 'Submitted feedback from the public form'
         ),  # For debaters, not tab assistants
        (ACTION_TYPE_FEEDBACK_SAVE,
         'Saved feedback'),  # For tab assistants, not debaters
        (ACTION_TYPE_TEST_SCORE_EDIT, 'Edited adjudicator test score'),
        (ACTION_TYPE_ADJUDICATORS_SAVE, 'Saved adjudicator allocation'),
        (ACTION_TYPE_VENUES_SAVE, 'Saved venues'),
        (ACTION_TYPE_DRAW_CREATE, 'Created draw'),
        (ACTION_TYPE_DRAW_CONFIRM, 'Confirmed draw'),
        (ACTION_TYPE_DRAW_RELEASE, 'Released draw'),
        (ACTION_TYPE_DRAW_UNRELEASE, 'Unreleased draw'),
        (ACTION_TYPE_DRAW_UNRELEASE, 'Saved divisions'),
        (ACTION_TYPE_MOTION_EDIT, 'Added/edited motion'),
        (ACTION_TYPE_MOTIONS_RELEASE, 'Released motions'),
        (ACTION_TYPE_MOTIONS_UNRELEASE, 'Unreleased motions'),
        (ACTION_TYPE_DEBATE_IMPORTANCE_EDIT, 'Edited debate importance'),
        (ACTION_TYPE_BREAK_ELIGIBILITY_EDIT, 'Edited break eligibility'),
        (ACTION_TYPE_BREAK_GENERATE_ALL,
         'Generated the teams break for all categories'),
        (ACTION_TYPE_BREAK_UPDATE_ALL,
         'Updated the teams break for all categories'),
        (ACTION_TYPE_BREAK_UPDATE_ONE, 'Updated the teams break'),
        (ACTION_TYPE_BREAK_EDIT_REMARKS, 'Edited breaking team remarks'),
        (ACTION_TYPE_ROUND_START_TIME_SET, 'Set start time'),
        (ACTION_TYPE_AVAIL_TEAMS_SAVE, 'Edited teams availability'),
        (ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE,
         'Edited adjudicators availability'),
        (ACTION_TYPE_AVAIL_VENUES_SAVE, 'Edited venue availability'),
        (ACTION_TYPE_OPTIONS_EDIT, 'Edited tournament options'), )

    REQUIRED_FIELDS_BY_ACTION_TYPE = {
        ACTION_TYPE_BALLOT_DISCARD: ('ballot_submission', ),
        ACTION_TYPE_BALLOT_CHECKIN: ('debate', ),  # not ballot_submission
        ACTION_TYPE_BALLOT_CREATE: ('ballot_submission', ),
        ACTION_TYPE_BALLOT_EDIT: ('ballot_submission', ),
        ACTION_TYPE_BALLOT_CONFIRM: ('ballot_submission', ),
        ACTION_TYPE_BALLOT_SUBMIT: ('ballot_submission', ),
        ACTION_TYPE_FEEDBACK_SUBMIT: ('adjudicator_feedback', ),
        ACTION_TYPE_FEEDBACK_SAVE: ('adjudicator_feedback', ),
        ACTION_TYPE_TEST_SCORE_EDIT: ('adjudicator_test_score_history', ),
        ACTION_TYPE_ADJUDICATORS_SAVE: ('round', ),
        ACTION_TYPE_VENUES_SAVE: ('round', ),
        ACTION_TYPE_DRAW_CREATE: ('round', ),
        ACTION_TYPE_DRAW_CONFIRM: ('round', ),
        ACTION_TYPE_DRAW_RELEASE: ('round', ),
        ACTION_TYPE_DRAW_UNRELEASE: ('round', ),
        ACTION_TYPE_DEBATE_IMPORTANCE_EDIT: ('debate', ),
        ACTION_TYPE_BREAK_ELIGIBILITY_EDIT: (),
        ACTION_TYPE_BREAK_GENERATE_ALL: (),
        ACTION_TYPE_BREAK_UPDATE_ALL: (),
        ACTION_TYPE_BREAK_UPDATE_ONE: ('break_category', ),
        ACTION_TYPE_BREAK_EDIT_REMARKS: (),
        ACTION_TYPE_ROUND_START_TIME_SET: ('round', ),
        ACTION_TYPE_MOTION_EDIT: ('motion', ),
        ACTION_TYPE_MOTIONS_RELEASE: ('round', ),
        ACTION_TYPE_MOTIONS_UNRELEASE: ('round', ),
        ACTION_TYPE_OPTIONS_EDIT: (),
        ACTION_TYPE_AVAIL_TEAMS_SAVE: ('round', ),
        ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE: ('round', ),
        ACTION_TYPE_AVAIL_VENUES_SAVE: ('round', ),
    }

    ALL_OPTIONAL_FIELDS = ('debate', 'ballot_submission',
                           'adjudicator_feedback', 'round', 'motion',
                           'break_category')

    type = models.CharField(max_length=10, choices=ACTION_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    tournament = models.ForeignKey('tournaments.Tournament',
                                   blank=True,
                                   null=True)

    debate = models.ForeignKey('draw.Debate', blank=True, null=True)
    ballot_submission = models.ForeignKey('results.BallotSubmission',
                                          blank=True,
                                          null=True)
    adjudicator_test_score_history = models.ForeignKey(
        'adjfeedback.AdjudicatorTestScoreHistory',
        blank=True,
        null=True)
    adjudicator_feedback = models.ForeignKey('adjfeedback.AdjudicatorFeedback',
                                             blank=True,
                                             null=True)
    round = models.ForeignKey('tournaments.Round', blank=True, null=True)
    motion = models.ForeignKey('motions.Motion', blank=True, null=True)
    break_category = models.ForeignKey('breakqual.BreakCategory',
                                       blank=True,
                                       null=True)

    objects = ActionLogManager()

    class Meta:
        verbose_name = "🕐 Action Log Entry"
        verbose_name_plural = "🕐 Action Log Entries"

    def __repr__(self):
        return '<Action %d by %s (%s): %s>' % (
            self.id, self.user, self.timestamp, self.get_type_display())

    def clean(self):
        try:
            required_fields = self.REQUIRED_FIELDS_BY_ACTION_TYPE[self.type]
        except KeyError:
            raise ValidationError("Unknown action type: %d" % self.type)

        errors = list()
        for field_name in self.ALL_OPTIONAL_FIELDS:
            if field_name in required_fields:
                if getattr(self, field_name) is None:
                    errors.append(ValidationError(
                        'A log entry of type "%s" requires the field "%s".' % (
                            self.get_type_display(), field_name)))
            else:
                if getattr(self, field_name) is not None:
                    errors.append(ValidationError(
                        'A log entry of type "%s" must not have the field "%s".'
                        % (self.get_type_display(), field_name)))
        if self.user is None and self.ip_address is None:
            errors.append(ValidationError(
                'All log entries require at least one of a user and an IP address.'))

        if errors:
            raise ValidationError(errors)

    def get_parameters_display(self):
        try:
            required_fields = self.REQUIRED_FIELDS_BY_ACTION_TYPE[self.type]
        except KeyError:
            return ""
        strings = list()
        for field_name in required_fields:
            try:
                value = getattr(self, field_name)
                if field_name == 'ballot_submission':
                    strings.append('%s vs %s' %
                                   (value.debate.aff_team.short_name,
                                    value.debate.neg_team.short_name))
                elif field_name == 'debate':
                    strings.append('%s vs %s' % (value.aff_team.short_name,
                                                 value.neg_team.short_name))
                elif field_name == 'round':
                    strings.append(value.name)
                elif field_name == 'motion':
                    strings.append(value.reference)
                elif field_name == 'adjudicator_test_score_history':
                    strings.append(value.adjudicator.name + " (" + str(
                        value.score) + ")")
                elif field_name == 'adjudicator_feedback':
                    strings.append(value.adjudicator.name)
                elif field_name == 'break_category':
                    strings.append(value.name)
                else:
                    strings.append(str(value))
            except AttributeError:
                strings.append("Unknown " + field_name)
        return ", ".join(strings)
