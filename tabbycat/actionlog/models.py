from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from options.utils import use_team_code_names
from utils.misc import badge_datetime_format


class ActionLogManager(models.Manager):
    def log(self, *args, **kwargs):
        obj = self.model(*args, **kwargs)
        obj.full_clean()
        obj.save()
        return obj


class ActionLogEntry(models.Model):
    # These aren't generated automatically - all generations of these should
    # be done in views (not models).

    ACTION_TYPE_BALLOT_CHECKIN                    = 'ba.ckin'
    ACTION_TYPE_BALLOT_CREATE                     = 'ba.crea'
    ACTION_TYPE_BALLOT_CONFIRM                    = 'ba.conf'
    ACTION_TYPE_BALLOT_DISCARD                    = 'ba.disc'
    ACTION_TYPE_BALLOT_SUBMIT                     = 'ba.subm'
    ACTION_TYPE_BALLOT_EDIT                       = 'ba.edit'
    ACTION_TYPE_FEEDBACK_SUBMIT                   = 'fb.subm'
    ACTION_TYPE_FEEDBACK_SAVE                     = 'fb.save'
    ACTION_TYPE_TEST_SCORE_EDIT                   = 'ts.edit'
    ACTION_TYPE_ADJUDICATOR_NOTE_SET              = 'aj.note'   # obsolete
    ACTION_TYPE_DRAW_CREATE                       = 'dr.crea'
    ACTION_TYPE_DRAW_CONFIRM                      = 'dr.conf'
    ACTION_TYPE_DRAW_REGENERATE                   = 'dr.rege'
    ACTION_TYPE_ADJUDICATORS_SAVE                 = 'aa.save'
    ACTION_TYPE_ADJUDICATORS_AUTO                 = 'aa.auto'
    ACTION_TYPE_VENUES_SAVE                       = 've.save'
    ACTION_TYPE_VENUES_AUTOALLOCATE               = 've.auto'
    ACTION_TYPE_VENUE_CATEGORIES_EDIT             = 've.ca.edit'
    ACTION_TYPE_VENUE_CONSTRAINTS_EDIT            = 've.co.edit'
    ACTION_TYPE_MATCHUP_SAVE                      = 'mu.save'
    ACTION_TYPE_SIDES_SAVE                        = 'ms.save'
    ACTION_TYPE_DRAW_RELEASE                      = 'dr.rele'
    ACTION_TYPE_DRAW_UNRELEASE                    = 'dr.unre'
    ACTION_TYPE_DIVISIONS_SAVE                    = 'dv.save'   # obsolete
    ACTION_TYPE_MOTION_EDIT                       = 'mo.edit'
    ACTION_TYPE_MOTIONS_RELEASE                   = 'mo.rele'
    ACTION_TYPE_MOTIONS_UNRELEASE                 = 'mo.unre'
    ACTION_TYPE_DEBATE_IMPORTANCE_AUTO            = 'db.im.auto'
    ACTION_TYPE_DEBATE_IMPORTANCE_EDIT            = 'db.im.edit'
    ACTION_TYPE_ROUND_START_TIME_SET              = 'rd.st.set'
    ACTION_TYPE_ROUND_ADVANCE                     = 'rd.adva'   # obsolete, kept to avoid breaking old sites
    ACTION_TYPE_ROUND_COMPLETE                    = 'rd.comp'
    ACTION_TYPE_ADJUDICATOR_BREAK_SET             = 'br.aj.set'
    ACTION_TYPE_BREAK_ELIGIBILITY_EDIT            = 'br.el.edit'
    ACTION_TYPE_BREAK_CATEGORIES_EDIT             = 'br.ca.edit'
    ACTION_TYPE_BREAK_GENERATE_ALL                = 'br.gene'
    ACTION_TYPE_BREAK_UPDATE_ALL                  = 'br.upda'
    ACTION_TYPE_BREAK_UPDATE_ONE                  = 'br.upd1'
    ACTION_TYPE_BREAK_EDIT_REMARKS                = 'br.rm.edit'
    ACTION_TYPE_AVAIL_TEAMS_SAVE                  = 'av.tm.save'
    ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE           = 'av.aj.save'
    ACTION_TYPE_AVAIL_VENUES_SAVE                 = 'av.ve.save'
    ACTION_TYPE_OPTIONS_EDIT                      = 'op.edit'
    ACTION_TYPE_SPEAKER_ELIGIBILITY_EDIT          = 'se.edit'
    ACTION_TYPE_SPEAKER_CATEGORIES_EDIT           = 'se.ca.edit'
    ACTION_TYPE_SIMPLE_IMPORT_INSTITUTIONS        = 'si.inst'
    ACTION_TYPE_SIMPLE_IMPORT_VENUES              = 'si.venu'
    ACTION_TYPE_SIMPLE_IMPORT_TEAMS               = 'si.team'
    ACTION_TYPE_SIMPLE_IMPORT_ADJUDICATORS        = 'si.adju'
    ACTION_TYPE_UPDATE_ADJUDICATOR_SCORES         = 'aj.sc.upda'
    ACTION_TYPE_CONFLICTS_ADJ_TEAM_EDIT           = 'ac.at.edit'
    ACTION_TYPE_CONFLICTS_ADJ_ADJ_EDIT            = 'ac.aa.edit'
    ACTION_TYPE_CONFLICTS_ADJ_INST_EDIT           = 'ac.ai.edit'
    ACTION_TYPE_CONFLICTS_TEAM_INST_EDIT          = 'ac.ti.edit'
    ACTION_TYPE_CHECKIN_SPEAK_GENERATE            = 'ch.sp.gene'
    ACTION_TYPE_CHECKIN_ADJ_GENERATE              = 'ch.aj.gene'
    ACTION_TYPE_CHECKIN_VENUES_GENERATE           = 'ch.ve.gene'
    ACTION_TYPE_PREFORMED_PANELS_CREATE           = 'pp.crea'
    ACTION_TYPE_PREFORMED_PANELS_IMPORTANCE_AUTO  = 'pp.im.auto'
    ACTION_TYPE_PREFORMED_PANELS_IMPORTANCE_EDIT  = 'pp.im.edit'
    ACTION_TYPE_PREFORMED_PANELS_ADJUDICATOR_AUTO = 'pp.aj.auto'
    ACTION_TYPE_PREFORMED_PANELS_ADJUDICATOR_EDIT = 'pp.aj.auto'
    ACTION_TYPE_PREFORMED_PANELS_DEBATES_AUTO     = 'pp.db.auto'

    ACTION_TYPE_CHOICES = (
        (ACTION_TYPE_BALLOT_DISCARD                   , _("Discarded ballot set")),
        (ACTION_TYPE_BALLOT_CHECKIN                   , _("Checked in ballot set")),
        (ACTION_TYPE_BALLOT_CREATE                    , _("Created ballot set")),  # For tab assistants, not debaters
        (ACTION_TYPE_BALLOT_EDIT                      , _("Edited ballot set")),
        (ACTION_TYPE_BALLOT_CONFIRM                   , _("Confirmed ballot set")),
        (ACTION_TYPE_BALLOT_SUBMIT                    , _("Submitted ballot set from the public form")),  # For debaters, not tab assistants
        (ACTION_TYPE_FEEDBACK_SUBMIT                  , _("Submitted feedback from the public form")),  # For debaters, not tab assistants
        (ACTION_TYPE_FEEDBACK_SAVE                    , _("Saved feedback")),  # For tab assistants, not debaters
        (ACTION_TYPE_TEST_SCORE_EDIT                  , _("Edited adjudicator base score")),
        (ACTION_TYPE_ADJUDICATOR_NOTE_SET             , _("Set adjudicator note")),
        (ACTION_TYPE_ADJUDICATORS_SAVE                , _("Saved adjudicator allocation")),
        (ACTION_TYPE_ADJUDICATORS_AUTO                , _("Auto-allocated adjudicators")),
        (ACTION_TYPE_VENUES_SAVE                      , _("Saved a room manual edit")),
        (ACTION_TYPE_VENUES_AUTOALLOCATE              , _("Auto-allocated rooms")),
        (ACTION_TYPE_VENUE_CATEGORIES_EDIT            , _("Edited room categories")),
        (ACTION_TYPE_VENUE_CONSTRAINTS_EDIT           , _("Edited room constraints")),
        (ACTION_TYPE_DRAW_CREATE                      , _("Created draw")),
        (ACTION_TYPE_DRAW_CONFIRM                     , _("Confirmed draw")),
        (ACTION_TYPE_DRAW_REGENERATE                  , _("Regenerated draw")),
        (ACTION_TYPE_DRAW_RELEASE                     , _("Released draw")),
        (ACTION_TYPE_DRAW_UNRELEASE                   , _("Unreleased draw")),
        (ACTION_TYPE_MATCHUP_SAVE                     , _("Saved a matchup manual edit")),
        (ACTION_TYPE_SIDES_SAVE                       , _("Saved the sides status of a matchup")),
        (ACTION_TYPE_DIVISIONS_SAVE                   , _("Saved divisions")),
        (ACTION_TYPE_MOTION_EDIT                      , _("Added/edited motion")),
        (ACTION_TYPE_MOTIONS_RELEASE                  , _("Released motions")),
        (ACTION_TYPE_MOTIONS_UNRELEASE                , _("Unreleased motions")),
        (ACTION_TYPE_DEBATE_IMPORTANCE_AUTO           , _("Auto-prioritized debate importance")),
        (ACTION_TYPE_DEBATE_IMPORTANCE_EDIT           , _("Edited debate importance")),
        (ACTION_TYPE_ADJUDICATOR_BREAK_SET            , _("Changed adjudicator breaking status")),
        (ACTION_TYPE_BREAK_ELIGIBILITY_EDIT           , _("Edited break eligibility")),
        (ACTION_TYPE_BREAK_CATEGORIES_EDIT            , _("Edited break categories")),
        (ACTION_TYPE_BREAK_GENERATE_ALL               , _("Generated the team break for all categories")),
        (ACTION_TYPE_BREAK_UPDATE_ALL                 , _("Edited breaking team remarks and updated all team breaks")),
        (ACTION_TYPE_BREAK_UPDATE_ONE                 , _("Edited breaking team remarks and updated this team break")),
        (ACTION_TYPE_BREAK_EDIT_REMARKS               , _("Edited breaking team remarks")),
        (ACTION_TYPE_ROUND_START_TIME_SET             , _("Set start time")),
        (ACTION_TYPE_ROUND_ADVANCE                    , _("Advanced the current round to")),
        (ACTION_TYPE_ROUND_COMPLETE                   , _("Marked round as completed")),
        (ACTION_TYPE_AVAIL_TEAMS_SAVE                 , _("Edited teams availability")),
        (ACTION_TYPE_AVAIL_ADJUDICATORS_SAVE          , _("Edited adjudicators availability")),
        (ACTION_TYPE_AVAIL_VENUES_SAVE                , _("Edited room availability")),
        (ACTION_TYPE_OPTIONS_EDIT                     , _("Edited tournament options")),
        (ACTION_TYPE_SPEAKER_ELIGIBILITY_EDIT         , _("Edited speaker category eligibility")),
        (ACTION_TYPE_SPEAKER_CATEGORIES_EDIT          , _("Edited speaker categories")),
        (ACTION_TYPE_SIMPLE_IMPORT_INSTITUTIONS       , _("Imported institutions using the simple importer")),
        (ACTION_TYPE_SIMPLE_IMPORT_VENUES             , _("Imported rooms using the simple importer")),
        (ACTION_TYPE_SIMPLE_IMPORT_TEAMS              , _("Imported teams using the simple importer")),
        (ACTION_TYPE_SIMPLE_IMPORT_ADJUDICATORS       , _("Imported adjudicators using the simple importer")),
        (ACTION_TYPE_UPDATE_ADJUDICATOR_SCORES        , _("Updated adjudicator scores in bulk")),
        (ACTION_TYPE_CONFLICTS_ADJ_TEAM_EDIT          , _("Edited adjudicator-team conflicts")),
        (ACTION_TYPE_CONFLICTS_ADJ_ADJ_EDIT           , _("Edited adjudicator-adjudicator conflicts")),
        (ACTION_TYPE_CONFLICTS_ADJ_INST_EDIT          , _("Edited adjudicator-institution conflicts")),
        (ACTION_TYPE_CONFLICTS_TEAM_INST_EDIT         , _("Edited team-institution conflicts")),
        (ACTION_TYPE_CHECKIN_SPEAK_GENERATE           , _("Generated check in identifiers for speakers")),
        (ACTION_TYPE_CHECKIN_ADJ_GENERATE             , _("Generated check in identifiers for adjudicators")),
        (ACTION_TYPE_CHECKIN_VENUES_GENERATE          , _("Generated check in identifiers for rooms")),
        (ACTION_TYPE_PREFORMED_PANELS_CREATE          , _("Created preformed panels")),
        (ACTION_TYPE_PREFORMED_PANELS_IMPORTANCE_AUTO , _("Auto-prioritized preformed panels")),
        (ACTION_TYPE_PREFORMED_PANELS_IMPORTANCE_EDIT , _("Edited preformed panel importance")),
        (ACTION_TYPE_PREFORMED_PANELS_ADJUDICATOR_AUTO, _("Auto-allocated adjudicators to preformed panels")),
        (ACTION_TYPE_PREFORMED_PANELS_ADJUDICATOR_EDIT, _("Edited preformed panel adjudicator")),
        (ACTION_TYPE_PREFORMED_PANELS_DEBATES_AUTO    , _("Auto-allocated preformed panels to debates")),
    )

    type = models.CharField(max_length=10, choices=ACTION_TYPE_CHOICES,
        verbose_name=_("type"))
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True,
        verbose_name=_("timestamp"))
    # cascade to avoid double-null user/ip-address
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, blank=True, null=True,
        verbose_name=_("user"))
    ip_address = models.GenericIPAddressField(blank=True, null=True,
        verbose_name=_("IP address"))

    # These fields are stored for convenience, and should be used only for filtering.
    tournament = models.ForeignKey('tournaments.Tournament', models.SET_NULL, blank=True, null=True,
        verbose_name=_("tournament"))
    round = models.ForeignKey('tournaments.Round', models.SET_NULL, blank=True, null=True,
        verbose_name=_("round"))

    # cascade to keep generic foreign keys complete where existent
    content_type = models.ForeignKey(ContentType, models.CASCADE, blank=True, null=True,
        verbose_name=_("content type"))
    object_id = models.PositiveIntegerField(blank=True, null=True,
        verbose_name=_("object ID"))
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = ActionLogManager()

    class Meta:
        verbose_name = _("action log")
        verbose_name_plural = _("action log entries")

    def __repr__(self):
        return '<Action %d by %s (%s): %s>' % (
            self.id, self.user, self.timestamp, self.get_type_display())

    def clean(self):
        if self.user is None and self.ip_address is None:
            raise ValidationError(_("All log entries require at least one of a user and an IP address."))

    def get_content_object_display(self, omit_tournament=False):
        obj = self.content_object

        if obj is None:
            return None

        model_name = self.content_type.model
        try:
            if model_name == 'ballotsubmission':
                if use_team_code_names(self.tournament, True):
                    return obj.debate.matchup_codes
                else:
                    return obj.debate.matchup
            elif model_name == 'debate':
                if use_team_code_names(self.tournament, True):
                    return obj.debate.matchup_codes
                else:
                    return obj.debate.matchup
            elif model_name == 'motion':
                return obj.reference
            elif model_name == 'adjudicatorbasescorehistory':
                return obj.adjudicator.name + " (" + str(obj.score) + ")"
            elif model_name == 'adjudicatorfeedback':
                return obj.adjudicator.name
            elif model_name == 'tournament':
                return None if omit_tournament else obj.name
            elif model_name in ['round', 'adjudicator', 'breakcategory']:
                return obj.name
            else:
                return str(obj)
        except Exception:
            return "<error displaying %s>" % model_name

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user': self.user.username if self.user else self.ip_address or _("anonymous"),
            'type': self.get_type_display(),
            'param': self.get_content_object_display(omit_tournament=True),
            'timestamp': badge_datetime_format(self.timestamp),
        }
