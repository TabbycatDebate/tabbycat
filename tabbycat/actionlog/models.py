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

    class ActionType(models.TextChoices):
        ADJUDICATOR_BREAK_SET             = 'br.aj.set', _("Changed adjudicator breaking status")
        ADJUDICATOR_CREATE                = 'aj.crea', _("Created adjudicator")
        ADJUDICATOR_EDIT                  = 'aj.edit', _("Edited adjudicator")
        ADJUDICATOR_NOTE_SET              = 'aj.note', _("Set adjudicator note")   # obsolete
        ADJUDICATORS_AUTO                 = 'aa.auto', _("Auto-allocated adjudicators")
        ADJUDICATORS_SAVE                 = 'aa.save', _("Saved adjudicator allocation")
        AVAIL_ADJUDICATORS_SAVE           = 'av.aj.save', _("Edited adjudicators availability")
        AVAIL_SAVE                        = 'av.save', _("Edited availability")
        AVAIL_TEAMS_SAVE                  = 'av.tm.save', _("Edited teams availability")
        AVAIL_VENUES_SAVE                 = 'av.ve.save', _("Edited room availability")
        BALLOT_CHECKIN                    = 'ba.ckin', _("Checked in ballot set")
        BALLOT_CONFIRM                    = 'ba.conf', _("Confirmed ballot set")
        BALLOT_CREATE                     = 'ba.crea', _("Created ballot set")
        BALLOT_DISCARD                    = 'ba.disc', _("Discarded ballot set")
        BALLOT_EDIT                       = 'ba.edit', _("Edited ballot set")
        BALLOT_SUBMIT                     = 'ba.subm', _("Submitted ballot set from the public form")
        BREAK_CATEGORIES_EDIT             = 'br.ca.edit', _("Edited break categories")
        BREAK_DELETE                      = 'br.del', _("Deleted team break for category")
        BREAK_EDIT_REMARKS                = 'br.rm.edit', _("Edited breaking team remarks")
        BREAK_ELIGIBILITY_EDIT            = 'br.el.edit', _("Edited break eligibility")
        BREAK_GENERATE_ALL                = 'br.gene', _("Generated the team break for all categories")
        BREAK_GENERATE_ONE                = 'br.gen1', _("Generated the team break for one category")
        BREAK_UPDATE_ALL                  = 'br.upda', _("Edited breaking team remarks and updated all team breaks")
        BREAK_UPDATE_ONE                  = 'br.upd1', _("Edited breaking team remarks and updated this team break")
        CHECKIN_ADJ_GENERATE              = 'ch.aj.gene', _("Generated check in identifiers for adjudicators")
        CHECKIN_SPEAK_GENERATE            = 'ch.sp.gene', _("Generated check in identifiers for speakers")
        CHECKIN_VENUES_GENERATE           = 'ch.ve.gene', _("Generated check in identifiers for rooms")
        CONFLICTS_ADJ_ADJ_EDIT            = 'ac.aa.edit', _("Edited adjudicator-adjudicator conflicts")
        CONFLICTS_ADJ_INST_EDIT           = 'ac.ai.edit', _("Edited adjudicator-institution conflicts")
        CONFLICTS_ADJ_TEAM_EDIT           = 'ac.at.edit', _("Edited adjudicator-team conflicts")
        CONFLICTS_TEAM_INST_EDIT          = 'ac.ti.edit', _("Edited team-institution conflicts")
        DEBATE_CREATE                     = 'db.crea', _("Created debate")
        DEBATE_EDIT                       = 'db.edit', _("Edited debate")
        DEBATE_IMPORTANCE_AUTO            = 'db.im.auto', _("Auto-prioritized debate importance")
        DEBATE_IMPORTANCE_EDIT            = 'db.im.edit', _("Edited debate importance")
        DIVISIONS_SAVE                    = 'dv.save', _("Saved divisions")   # obsolete
        DRAW_CONFIRM                      = 'dr.conf', _("Confirmed draw")
        DRAW_CREATE                       = 'dr.crea', _("Created draw")
        DRAW_REGENERATE                   = 'dr.rege', _("Regenerated draw")
        DRAW_RELEASE                      = 'dr.rele', _("Released draw")
        DRAW_UNRELEASE                    = 'dr.unre', _("Unreleased draw")
        FEEDBACK_QUESTION_CREATE          = 'fq.crea', _("Created feedback question")
        FEEDBACK_QUESTION_EDIT            = 'fq.edit', _("Edited feedback question")
        FEEDBACK_SAVE                     = 'fb.save', _("Saved feedback")
        FEEDBACK_SUBMIT                   = 'fb.subm', _("Submitted feedback from the public form")
        INSTITUTION_CREATE                = 'in.crea', _("Created institution")
        INSTITUTION_EDIT                  = 'in.edit', _("Edited institution")
        MATCHUP_SAVE                      = 'mu.save', _("Saved a matchup manual edit")
        MOTION_EDIT                       = 'mo.edit', _("Added/edited motion")
        MOTIONS_RELEASE                   = 'mo.rele', _("Released motions")
        MOTIONS_UNRELEASE                 = 'mo.unre', _("Unreleased motions")
        OPTIONS_EDIT                      = 'op.edit', _("Edited tournament options")
        PREFORMED_PANELS_ADJUDICATOR_AUTO = 'pp.aj.auto', _("Auto-allocated adjudicators to preformed panels")
        PREFORMED_PANELS_ADJUDICATOR_EDIT = 'pp.aj.edit', _("Edited preformed panel adjudicator")
        PREFORMED_PANELS_CREATE           = 'pp.crea', _("Created preformed panels")
        PREFORMED_PANELS_DEBATES_AUTO     = 'pp.db.auto', _("Auto-allocated preformed panels to debates")
        PREFORMED_PANELS_DELETE           = 'pp.del', _("Deleted preformed panels")
        PREFORMED_PANELS_IMPORTANCE_AUTO  = 'pp.im.auto', _("Auto-prioritized preformed panels")
        PREFORMED_PANELS_IMPORTANCE_EDIT  = 'pp.im.edit', _("Edited preformed panel importance")
        ROUND_ADVANCE                     = 'rd.adva', _("Advanced the current round to")   # obsolete
        ROUND_COMPLETE                    = 'rd.comp', _("Marked round as completed")
        ROUND_CREATE                      = 'rd.crea', _("Created round")
        ROUND_EDIT                        = 'rd.edit', _("Edited round")
        ROUND_START_TIME_SET              = 'rd.st.set', _("Set start time")
        SIDES_SAVE                        = 'ms.save', _("Saved the sides status of a matchup")
        SIMPLE_IMPORT_ADJUDICATORS        = 'si.adju', _("Imported adjudicators using the simple importer")
        SIMPLE_IMPORT_INSTITUTIONS        = 'si.inst', _("Imported institutions using the simple importer")
        SIMPLE_IMPORT_TEAMS               = 'si.team', _("Imported teams using the simple importer")
        SIMPLE_IMPORT_VENUES              = 'si.venu', _("Imported rooms using the simple importer")
        SPEAKER_CATEGORIES_EDIT           = 'se.ca.edit', _("Edited speaker categories")
        SPEAKER_CREATE                    = 'sp.crea', _("Created speaker")
        SPEAKER_EDIT                      = 'sp.edit', _("Edited speaker")
        SPEAKER_ELIGIBILITY_EDIT          = 'se.edit', _("Edited speaker category eligibility")
        TEAM_CREATE                       = 'te.crea', _("Created team")
        TEAM_EDIT                         = 'te.edit', _("Edited team")
        TEST_SCORE_EDIT                   = 'ts.edit', _("Edited adjudicator base score")
        TOURNAMENT_CREATE                 = 'to.crea', _("Created tournament")
        TOURNAMENT_EDIT                   = 'to.edit', _("Edited tournament")
        UPDATE_ADJUDICATOR_SCORES         = 'aj.sc.upda', _("Updated adjudicator scores in bulk")
        USER_INVITE                       = 'ur.inv', _("Invited user to the instance")
        VENUE_CATEGORIES_EDIT             = 've.ca.edit', _("Edited room categories")
        VENUE_CATEGORY_CREATE             = 've.ca.crea', _("Created room category")
        VENUE_CONSTRAINTS_EDIT            = 've.co.edit', _("Edited room constraints")
        VENUE_CREATE                      = 've.crea', _("Created room")
        VENUE_EDIT                        = 've.edit', _("Edited room")
        VENUES_AUTOALLOCATE               = 've.auto', _("Auto-allocated rooms")
        VENUES_SAVE                       = 've.save', _("Saved a room manual edit")

    class Agent(models.TextChoices):
        API = 'a', _("API")
        WEB = 'w', _("Web")

    type = models.CharField(max_length=10, choices=ActionType.choices,
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
    agent = models.CharField(max_length=1, choices=Agent.choices, default=Agent.WEB,
        verbose_name=_("agent"))

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

    def get_content_object_display(self, omit_tournament=False, user=None):
        obj = self.content_object

        if obj is None:
            return None

        model_name = self.content_type.model
        try:
            if model_name == 'ballotsubmission':
                if use_team_code_names(self.tournament, True, user):
                    return obj.debate.matchup_codes
                else:
                    return obj.debate.matchup
            elif model_name == 'debate':
                if use_team_code_names(self.tournament, True, user):
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
            # As the team names are passed in the content of the message for all users,
            # must assume they don't have permission for real names
            'param': self.get_content_object_display(omit_tournament=True, user=None),
            'timestamp': badge_datetime_format(self.timestamp),
        }
