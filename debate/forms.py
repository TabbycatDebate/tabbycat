from django import forms
from django.utils.translation import ugettext as _

from debate.models import SpeakerScoreByAdj, Debate, Motion, Round, Team, Adjudicator
from debate.models import DebateTeam, DebateAdjudicator, AdjudicatorFeedback
from debate.models import ActionLog
from debate.result import BallotSet

from collections import Counter

def get_or_instantiate(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return model(**kwargs)

### Result/ballot forms

class BaseScoreField(forms.FloatField):
    def __init__(self, tournament_config=None, *args, **kwargs):
        """Takes an additional optional keyword argument: tournament_config,
        the Config object for the Tournament."""

        if tournament_config:
            min_value  = tournament_config.get(self.CONFIG_MIN_VALUE_FIELD, default=self.DEFAULT_MIN_VALUE)
            max_value  = tournament_config.get(self.CONFIG_MAX_VALUE_FIELD, default=self.DEFAULT_MAX_VALUE)
            step_value = tournament_config.get(self.CONFIG_STEP_VALUE_FIELD, default=self.DEFAULT_STEP_VALUE)
        else:
            min_value  = self.DEFAULT_MIN_VALUE
            max_value  = self.DEFAULT_MAX_VALUE
            step_value = self.DEFAULT_STEP_VALUE
        self.step_value = kwargs.get('step_value', step_value)

        kwargs.setdefault('min_value', min_value)
        kwargs.setdefault('max_value', max_value)

        # Overwrite the "step" attribute.
        # Note, this overrides everything, so it means you can't set the
        # 'step' attribute of the widget directly - you must use the
        # step_value keyword argument.
        widget = kwargs.get('widget', self.widget)
        if isinstance(widget, type):
            widget = widget()
        if isinstance(widget, forms.NumberInput):
            widget.attrs['step'] = self.step_value
        kwargs['widget'] = widget

        super(BaseScoreField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(BaseScoreField, self).validate(value)
        self.check_value(value)

    def check_value(self, value):
        if value % self.step_value != 0:
            if self.step_value == 1:
                msg = 'Please enter a whole number.'
            else:
                msg = 'Please enter a multiple of %s.' % self.step_value
            raise forms.ValidationError(
                _(msg), code='decimal'
            )

class ScoreField(BaseScoreField):
    CONFIG_MIN_VALUE_FIELD  = 'score_min'
    CONFIG_MAX_VALUE_FIELD  = 'score_max'
    CONFIG_STEP_VALUE_FIELD = 'score_step'
    DEFAULT_MIN_VALUE = 68
    DEFAULT_MAX_VALUE = 82
    DEFAULT_STEP_VALUE = 1

class ReplyScoreField(BaseScoreField):
    CONFIG_MIN_VALUE_FIELD  = 'reply_score_min'
    CONFIG_MAX_VALUE_FIELD  = 'reply_score_max'
    CONFIG_STEP_VALUE_FIELD = 'reply_score_step'
    DEFAULT_MIN_VALUE = 34
    DEFAULT_MAX_VALUE = 41
    DEFAULT_STEP_VALUE = 0.5

class TournamentPasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        if 'tournament' in kwargs:
            tournament = kwargs.pop('tournament')
            self.password = tournament.config.get('public_password')
        else:
            raise TypeError("'tournament' is a required keyword argument")
        if 'label' not in kwargs:
            kwargs['label'] = "Tournament password"
        super(TournamentPasswordField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(TournamentPasswordField, self).clean(value)
        if value != self.password:
            raise forms.ValidationError(_("That password isn't correct."))
        return value

class BallotSetForm(forms.Form):
    """Form for data entry for a single set of ballots.
    Responsible for presenting the part that looks like a ballot, i.e.
    speaker names and scores for each adjudicator. Not responsible for
    controls that submit the form or anything like that.
    """

    confirmed = forms.BooleanField(required=False,
        widget = forms.CheckboxInput(attrs = {'tabindex': 100}))
    discarded = forms.BooleanField(required=False,
        widget = forms.CheckboxInput(attrs = {'tabindex': 101}))

    debate_result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES,
        widget = forms.Select(attrs = {'tabindex': 102}))

    def __init__(self, ballots, *args, **kwargs):
        """
        Dynamically generate fields for this ballot

        <side>_speaker_<pos> and
        <side>_score_<pos>
        """
        self.ballots = ballots
        self.debate = ballots.debate
        self.adjudicators = self.debate.adjudicators.list

        super(BallotSetForm, self).__init__(*args, **kwargs)

        # Grab info about how many positions there are
        tournament = self.debate.round.tournament
        self.POSITIONS = tournament.POSITIONS
        self.LAST_SUBSTANTIVE_POSITION = tournament.LAST_SUBSTANTIVE_POSITION
        self.REPLY_POSITION = tournament.REPLY_POSITION

        if tournament.config.get('public_use_password'):
            self.fields['password'] = TournamentPasswordField(tournament=tournament)

        # Generate the motions field.
        # We are only allowed to choose from the motions for this round.
        self.motions = self.debate.round.motion_set
        self.show_motion = self.motions.exists() # this is used in the template
        # Tab index for the motion field is first if there's more than one, or last if
        # there's only one.
        self.fields['motion'] = forms.ModelChoiceField(
            queryset = self.motions,
            widget   = forms.Select(attrs = {'tabindex': self.motions.count() > 1 and 1 or 1100}),
            required = True)

        # Set the initial data
        self.initial = self._initial_data()

        # Grab the relevant score field configurations
        config = tournament.config

        # tab indices are as follows (example):
        #
        # Adjudicator 1
        #  21 A1name  22 A1score    29 N1name  30 N1score
        #  23 A2name  24 A2score    31 N2name  32 N2score
        #  25 A3name  26 A3score    33 N3name  34 N3score
        #  27 ARname  28 ARscore    35 NRname  36 NRscore
        #
        # Adjudicator 2 (odd numbers not used)
        #   - A1name  38 A1score     - N1name  46 N1score
        #   - A2name  40 A2score     - N2name  48 N2score
        #   - A3name  42 A3score     - N3name  50 N3score
        #   - ARname  44 ARscore     - NRname  52 NRscore
        #
        # Adjudicator 3 (odd numbers not used)
        #   - A1name  54 A1score     - N1name  62 N1score
        #   - A2name  56 A2score     - N2name  64 N2score
        #   - A3name  58 A3score     - N3name  66 N3score
        #   - ARname  60 ARscore     - NRname  68 NRscore

        MAX_POSITION = max(self.POSITIONS)

        for side, tab_index_add in (('aff', 0), ('neg', 2 * MAX_POSITION)):

            team = self.debate.get_team(side)
            for pos in self.POSITIONS:
                self.fields['%s_speaker_%s' % (side, pos)] = forms.ModelChoiceField(
                    queryset = team.speakers,
                    widget = forms.Select(attrs = {
                        'tabindex': 19 + 2 * pos + tab_index_add,
                    }))

                # css_class is for jquery validation plugin, surely this can
                # be moved elsewhere
                score_field = (pos == self.REPLY_POSITION) and ReplyScoreField or ScoreField

                for i, adj in enumerate(self.adjudicators):
                    attrs = {
                        'class': 'required number',
                        'tabindex': 20 + 2 * pos + tab_index_add + 4 * MAX_POSITION * i,
                    }
                    self.fields[self.score_field_name(adj, side, pos)] = score_field(
                        widget = forms.NumberInput(attrs=attrs),
                        tournament_config=tournament.config, **kwargs)

    def score_field_name(self, adj, side, pos):
        """
        Return the name of the score field for adj/side/pos
        """
        return '%s_score_a%d_%d' % (side, adj.id, pos)

    def score_field(self, adj, side, pos):
        return self[self.score_field_name(adj, side, pos)]

    def _initial_data(self):
        """
        Generate dictionary of initial form data
        """

        initial = {'debate_result_status': self.debate.result_status}

        bs = BallotSet(self.ballots)

        initial['confirmed'] = bs.confirmed
        initial['discarded'] = bs.discarded

        # This isn't relevant if we're not showing the motions field
        # (i.e. there are no motions given for this round).
        # Generally, initialise the motion to what is currently in the
        # database.  But if there is only one motion and no motion is
        # currently stored in the database for this round, then default
        # to the only motion there is.
        if self.show_motion:
            if not bs.motion and self.motions.count() == 1:
                initial['motion'] = self.motions[0]
            else:
                initial['motion'] = bs.motion

        for side in ('aff', 'neg'):
            for i in self.POSITIONS:
                speaker = bs.get_speaker(side, i)
                if speaker:
                    initial['%s_speaker_%d' % (side, i)] = speaker.id

                    for adj in self.adjudicators:
                        score = bs.get_score(adj, side, i)
                        initial[self.score_field_name(adj, side, i)] = score

        return initial

    def clean(self):
        cleaned_data = super(BallotSetForm, self).clean()

        errors = list()

        # TODO this should go up to the BallotSubmission.full_clean() method.
        # Not sure how to structure this.
        # For now just implement the same checks here.
        if cleaned_data['discarded'] and cleaned_data['confirmed']:
            errors.append(forms.ValidationError(
                _('The ballot set can\'t be both discarded and confirmed.')
            ))
        if cleaned_data['debate_result_status'] == Debate.STATUS_CONFIRMED and not cleaned_data['confirmed'] and self.debate.confirmed_ballot is None:
            errors.append(forms.ValidationError(
                _('The debate status can\'t be confirmed unless one of the ballot sets is confirmed.')
            ))
        # end TODO

        for adj in self.adjudicators:
            # Check that it was not a draw
            try:
                aff_total = sum(cleaned_data[self.score_field_name(adj, 'aff', pos)] for pos in self.POSITIONS)
                neg_total = sum(cleaned_data[self.score_field_name(adj, 'neg', pos)] for pos in self.POSITIONS)
            except KeyError:
                continue
            if aff_total == neg_total:
                errors.append(forms.ValidationError(
                    _('The total scores for the teams are the same (i.e. a draw) for adjudicator %(adj)s (%(adj_ins)s)'),
                    params={'adj': adj.name, 'adj_ins': adj.institution.code}, code='draw'
                ))

        for side in ('affirmative', 'negative'):
            # The three speaker fields must be unique.
            speakers = Counter()
            for i in xrange(1, self.LAST_SUBSTANTIVE_POSITION + 1):
                try:
                    speaker = cleaned_data['%s_speaker_%d' % (side[:3], i)]
                except KeyError:
                    continue
                speakers[speaker] += 1
            for speaker, count in speakers.iteritems():
                if count > 1:
                    errors.append(forms.ValidationError(
                        _('The speaker %(speaker)s appears to have given multiple (%(count)d) substantive speeches for the %(side)s team.'),
                        params={'speaker': speaker, 'side': side, 'count': count}, code='speaker'
                    ))

            # The third speaker can't give the reply.
            try:
                reply_speaker_error = cleaned_data['%s_speaker_%d' % (side[:3], self.LAST_SUBSTANTIVE_POSITION)] \
                        == cleaned_data['%s_speaker_%d' % (side[:3], self.REPLY_POSITION)]
            except KeyError:
                continue
            if reply_speaker_error:
                errors.append(forms.ValidationError(
                    _('The last substantive speaker and reply speaker for the %(side)s team are the same.'),
                    params={'side': side}, code='reply_speaker'
                ))

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

    def save(self):
        # Unconfirm the other, if necessary
        if self.cleaned_data['confirmed']:
            if self.debate.confirmed_ballot != self.ballots and self.debate.confirmed_ballot is not None:
                self.debate.confirmed_ballot.confirmed = False
                self.debate.confirmed_ballot.save()

        bs = BallotSet(self.ballots)

        def do(side):
            for i in self.POSITIONS:
                speaker = self.cleaned_data['%s_speaker_%d' % (side, i)]
                bs.set_speaker(side, i, speaker)
                for adj in self.adjudicators:
                    score = self.cleaned_data[self.score_field_name(adj, side, i)]
                    bs.set_score(adj, side, i, score)
        do('aff')
        do('neg')

        bs.motion    = self.cleaned_data['motion']
        bs.discarded = self.cleaned_data['discarded']
        bs.confirmed = self.cleaned_data['confirmed']

        bs.save()

        self.debate.result_status = self.cleaned_data['debate_result_status']
        self.debate.save()

    def adj_iter(self):
        form = self

        class Position(object):
            def __init__(self, adj, pos, name):
                self.adj = adj
                self.pos = pos
                self.name = name

            def __unicode__(self):
                return unicode(self.name)

            def aff_speaker(self):
                return form['aff_speaker_%d' % self.pos]

            def neg_speaker(self):
                return form['neg_speaker_%d' % self.pos]

            def _scores(self, side):
                for adj in form.adjudicators:
                    yield form.score_field(adj, side, self.pos)

            def aff_score(self):
                return str(form.score_field(self.adj, 'aff', self.pos))

            def aff_score_errors(self):
                return str(form.score_field(self.adj, 'aff', self.pos).errors)

            def neg_score(self):
                return str(form.score_field(self.adj, 'neg', self.pos))

            def neg_score_errors(self):
                return str(form.score_field(self.adj, 'neg', self.pos).errors)

        class AdjudicatorWrapper(object):
            def __init__(self, adj):
                self.adj = adj

            def position_iter(self):
                for i in form.POSITIONS:
                    name = (i == form.REPLY_POSITION) and "Reply" or str(i)
                    yield Position(self.adj, i, name)


        for adj in self.adjudicators:
            yield AdjudicatorWrapper(adj)


class DebateManagementForm(forms.Form):
    """ NOT CURRENTLY USED
    Traditionally, a Django FormSet has a ManagementForm to keep track of the
    forms on the page. In a debate result, there are some fields the relate to the
    debate as a whole, not an individual ballot. This form is responsible for those
    fields, and is always part of a DebateResultFormSet."""

    result_status = forms.ChoiceField(choices=Debate.STATUS_CHOICES,
        widget = forms.Select(attrs = {'tabindex': 1000}))

    def __init__(self, debate, *args, **kwargs):
        self.debate = debate

        super(DebateManagementForm, self).__init__(*args, **kwargs)

        self.initial['result_status'] = self.debate.result_status

        # Generate the confirmed ballot field
        self.fields['confirmed_ballot'] = forms.ModelChoiceField(
            queryset = self.debate.ballotsubmission_set,
            widget   = forms.Select(attrs = {'tabindex': 2}),
            required = False)
        self.initial['confirmed_ballot'] = self.debate.confirmed_ballot

    def save(self):
        # Unconfirm the old ballot
        # (Technically, we could rely on BallotSubmission.save() to do this
        # for us, but it's better to be explicit than rely on a backup check.)
        old_confirmed_ballot = self.debate.confirmed_ballot
        old_confirmed_ballot.confirmed = False
        old_confirmed_ballot.save()

        # Confirm the new ballot
        new_confirmed_ballot = self.cleaned_data['confirmed_ballot']
        new_confirmed_ballot.confirmed = True
        new_confirmed_ballot.save()

        # Update the debate status
        # TODO catch validation errors
        self.debate.result_status = self.cleaned_data['result_status']
        self.debate.save()

class DebateResultFormSet(object):
    """ NOT CURRENTLY USED
    A manager for the various forms that comprise a debate result form.

    This should only be used with tab room interfaces. The public should never
    see anything remotely resembling this form set.

    In many ways, this is similar to FormSet. But it adds too much functionality
    specific to debate results, including managing relationships between forms,
    and uses too little of BaseFormSet's actual functionality, to be worth
    inheriting from BaseFormSet. Maybe we'll eventually change this."""

    # TODO Add a ManagementForm to this, if we ever want to add/delete forms using JavaScript

    def __init__(self, debate, data=None, *args, **kwargs):
        """Dynamically generate the ballot set forms for this debate.
        Basically we do this by initializing the data of the formset."""

        self.debate_management_form = DebateManagementForm(debate)
        self.ballotset_forms = list()

        for ballot in debate.ballotsubmission_set.all():
            form = BallotSetForm(ballot)
            self.ballotset_forms.append(form)

    def save(self):
        pass

### Feedback forms

class RequiredTypedChoiceField(forms.TypedChoiceField):
    def clean(self, value):
        value = super(forms.TypedChoiceField, self).clean(value)
        if value == "None":
            raise forms.ValidationError(_("This field is required."))
        return value

def make_feedback_form_class_for_tabroom(adjudicator, submission_fields, released_only=False):
    """adjudicator is an Adjudicator.
    submission_fields is a dict of fields for Submission.
    released_only is a boolean."""

    if released_only:
        das = DebateAdjudicator.objects.filter(adjudicator = adjudicator,
            debate__round__draw_status = Round.STATUS_RELEASED)
    else:
        das = DebateAdjudicator.objects.filter(adjudicator = adjudicator)

    debates = [da.debate for da in das]

    def adj_choice(da):
        return (
            'A:%d' % da.id,
            '%s (R%d, %s)' % (da.adjudicator.name, da.debate.round.seq,
                           da.get_type_display())
        )

    adj_choices = [(None, '-- Adjudicators --')]
    adj_choices.extend ([
        adj_choice(da) for da in DebateAdjudicator.objects.filter(
            debate__id__in = [d.id for d in debates]
        ).select_related('debate') if da.adjudicator != adjudicator
    ])

    # Get rid of the heading if there aren't any adjudicators
    if len(adj_choices) == 1: adj_choices = []

    def team_choice(dt):
        return (
            'T:%d' % dt.id,
            '%s (%d)' % (dt.team.short_name, dt.debate.round.seq)
        )

    team_choices = [(None, '-- Teams --')]
    team_choices.extend([
        team_choice(dt) for dt in DebateTeam.objects.filter(
            debate__id__in = [d.id for d in debates]
        ).select_related('debate')
    ])

    choices = adj_choices + team_choices

    def coerce(value):
        obj_type, id = value.split(':')
        id = int(id)

        if obj_type.strip() == 'A':
            return DebateAdjudicator.objects.get(id=id)
        if obj_type.strip() == 'T':
            return DebateTeam.objects.get(id=id)

    tournament = adjudicator.institution.tournament

    class FeedbackForm(forms.Form):
        source = RequiredTypedChoiceField(
            choices = choices,
            # Bug in Django 1.6.5, see https://code.djangoproject.com/ticket/21397
            # Fix when Django 1.7 is released.
            #coerce = coerce,
        )

        score = forms.FloatField(
            min_value = 1,
            max_value = 5,
        )

        comment = forms.CharField(widget=forms.Textarea, required=False)

        def __init__(self, *args, **kwargs):
            super(FeedbackForm, self).__init__(*args, **kwargs)
            if tournament.config.get('public_use_password'):
                self.fields['password'] = TournamentPasswordField(tournament=tournament)

        def save(self):
            # Saves the form and returns the AdjudicatorFeedback object

            source = self.cleaned_data['source']
            source = coerce(source) # Bug in Django 1.6.5

            if isinstance(source, DebateAdjudicator):
                sa = source
            else:
                sa = None
            if isinstance(source, DebateTeam):
                st = source
            else:
                st = None

            # Discard existing feedbacks
            for fb in AdjudicatorFeedback.objects.filter(adjudicator=adjudicator,
                    source_adjudicator=sa, source_team=st):
                fb.discarded = True
                fb.save()

            # Save the new one
            af = AdjudicatorFeedback(
                adjudicator       =adjudicator,
                source_adjudicator=sa,
                source_team       =st,
                confirmed         =True, # assume confirmed on every submission
                **submission_fields
            )

            af.score = self.cleaned_data['score']
            af.comments = self.cleaned_data['comment']

            af.save()

            return af

    return FeedbackForm

def make_feedback_form_class_for_public_adj(source, submission_fields, include_panellists=True):

    kwargs = dict()
    kwargs['debate__round__draw_status'] = Round.STATUS_RELEASED

    def adj_choice(da):
        return (
            da.id,
            '%s (R%d, %s)' % (da.adjudicator.name, da.debate.round.seq,
                           da.get_type_display())
        )
    choices = [(None, '-- Adjudicators --')]

    if not include_panellists:
        # Include only debates for which this adj was the chair.
        kwargs['type'] = DebateAdjudicator.TYPE_CHAIR

    debates = [da.debate for da in DebateAdjudicator.objects.filter(
        adjudicator=source, **kwargs).select_related('debate')]

    # For an adjudicator, find every adjudicator on their panel except them.
    choices.extend([
        adj_choice(da) for da in DebateAdjudicator.objects.filter(
            debate__id__in = [d.id for d in debates]
        ).select_related('debate').order_by('debate__round') if da.adjudicator != source
    ])

    def coerce(value):
        value = int(value)
        return DebateAdjudicator.objects.get(id=value)

    tournament = source.institution.tournament

    class FeedbackForm(forms.Form):
        debate_adjudicator = RequiredTypedChoiceField(
            choices = choices,
            # Bug in Django 1.6.5, see https://code.djangoproject.com/ticket/21397
            # Fix when Django 1.7 is released.
            #coerce = coerce,
        )

        score = forms.FloatField(
            min_value = 1,
            max_value = 5,
        )

        comment = forms.CharField(widget=forms.Textarea, required=False)

        def __init__(self, *args, **kwargs):
            super(FeedbackForm, self).__init__(*args, **kwargs)
            if tournament.config.get('public_use_password'):
                self.fields['password'] = TournamentPasswordField(tournament=tournament)

        def save(self):
            # Saves the form and returns the AdjudicatorFeedback object

            da = self.cleaned_data['debate_adjudicator']
            da = coerce(da) # Bug in Django 1.6.5

            sa = DebateAdjudicator.objects.get(adjudicator=source, debate=da.debate)

            af = AdjudicatorFeedback(
                adjudicator       =da.adjudicator,
                source_adjudicator=sa,
                source_team       =None,
                **submission_fields
            )

            af.score = self.cleaned_data['score']
            af.comments = self.cleaned_data['comment']

            af.save()

            return af

    return FeedbackForm

def make_feedback_form_class_for_public_team(source, submission_fields, include_panellists=True):
    """source is an Adjudicator or Team.
    submission_fields is a dict of fields for Submission.
    released_only is a boolean."""

    choices = [(None, '-- Adjudicators --')]

    # Only include non-silent rounds for teams.
    debates = [dt.debate for dt in DebateTeam.objects.filter(
        team=source, debate__round__silent=False,
        debate__round__draw_status=Round.STATUS_RELEASED).select_related('debate')]

    for debate in debates:
        try:
            chair = DebateAdjudicator.objects.get(debate=debate, type=DebateAdjudicator.TYPE_CHAIR)
        except DebateAdjudicator.DoesNotExist:
            continue
        panel = DebateAdjudicator.objects.filter(debate=debate, type=DebateAdjudicator.TYPE_PANEL)
        if panel.exists():
            choices.append((chair.id, '{name} (R{r} - chair gave oral)'.format(
                name=chair.adjudicator.name, r=debate.round.seq)))
            for da in panel:
                choices.append((da.id, '{name} (R{r} - chair rolled, this panellist gave oral)'.format(
                    name=da.adjudicator.name, r=debate.round.seq)))
        else:
            choices.append((chair.id, '{name} (R{r})'.format(
                name=chair.adjudicator.name, r=debate.round.seq)))

    def coerce(value):
        value = int(value)
        return DebateAdjudicator.objects.get(id=value)

    tournament = source.institution.tournament

    class FeedbackForm(forms.Form):
        debate_adjudicator = RequiredTypedChoiceField(
            choices = choices,
            # Bug in Django 1.6.5, see https://code.djangoproject.com/ticket/21397
            # Fix when Django 1.7 is released.
            #coerce = coerce,
        )

        score = forms.FloatField(
            min_value = 1,
            max_value = 5,
        )

        comment = forms.CharField(widget=forms.Textarea, required=False)

        def __init__(self, *args, **kwargs):
            super(FeedbackForm, self).__init__(*args, **kwargs)
            if tournament.config.get('public_use_password'):
                self.fields['password'] = TournamentPasswordField(tournament=tournament)

        def save(self):
            # Saves the form and returns the AdjudicatorFeedback object

            da = self.cleaned_data['debate_adjudicator']
            da = coerce(da) # Bug in Django 1.6.5

            st = DebateTeam.objects.get(team=source, debate=da.debate)

            af = AdjudicatorFeedback(
                adjudicator       =da.adjudicator,
                source_adjudicator=None,
                source_team       =st,
                **submission_fields
            )

            af.score = self.cleaned_data['score']
            af.comments = self.cleaned_data['comment']

            af.save()

            return af

    return FeedbackForm

def test():
    from debate.models import Debate

    return make_results_form_class(Debate.objects.get(pk=1))
