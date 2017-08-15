<template>
  <div class="db-flex-column db-flex-item-1">

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-fhs db-flex-static"
             v-if="ballot.debateAdjudicators && ballot.debateAdjudicators.length > 1">
      <div class="db-padding-horizontal db-align-vertical-center db-vertical-center-text">
        The other adjudicators are
        <span v-for="(da, i) in panellistsExcludingSelf">
          <span v-if="i !== 0">&nbsp;and</span>&nbsp;<strong>{{ da.adjudicator.name }}</strong>
          <span v-if="da.position === 'C'">
            (Chair, {{ da.adjudicator.institution.code }})
          </span>
          <span v-if="da.position === 'O'">
            (Solo Chair, {{ da.adjudicator.institution.code }})
          </span>
          <span v-if="da.position === 'P'">
            (Panellist, {{ da.adjudicator.institution.code }})
          </span>
          <span v-if="da.position === 'T'">
            (Trainee, {{ da.adjudicator.institution.code }})
          </span>
        </span>.
      </div>
    </section>

    <section v-if="!roundInfo.hasMotions" class="db-margins-m db-bordered db-flex-row db-flex-item-fhs db-flex-static">
      <div class="db-padding-horizontal db-align-vertical-center db-vertical-center-text">
        <span>The motion is <em>{{ roundInfo.motions[0].text }}.</em></span>
      </div>
    </section>

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1"
             v-if="roundInfo.hasMotions && !roundInfo.hasVetoes">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
          Motion:
        </div>
        <div class="db-flex-item db-align-vertical-center" v-if="roundInfo.motions[0]">
          <em>{{ motions[0].text }}</em>
        </div>
        <div v-else class="db-flex-item db-padding-horizontal db-fill-in"></div>
      </div>
    </section>

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1"
             v-if="roundInfo.hasMotions">

      <div class="db-padding-horizontal db-flex-item-1 db-flex-row"
           v-if="roundInfo.hasVetoes">
        <div v-for="choice_type in ['Chosen Motion', 'Aff Veto', 'Neg Veto']" class="db-flex-item-1 db-flex-column">
          <div class="db-flex-item-2 db-align-horizontal-center db-align-vertical-end" v-html="choice_type"></div>
          <div class="db-flex-item-1 "></div>
          <div class="db-flex-item-2 db-flex-row">
            <div class="db-item-gutter"></div>
            <div v-for="motion in motionsAccountingForBlanks"
                 class="db-align-horizontal-center db-align-vertical-start db-flex-item-1 db-center-text">
              <span class="db-fill-in">{{ motion.seq }}</span>
            </div>
            <div class="db-item-gutter"></div>
          </div>
        </div>
      </div>

      <div class="db-item-gutter"></div>
      <div class="db-flex-item-2 db-flex-row db-align-vertical-center">
        <template v-for="(motion, index) in roundInfo.motions">
          {{ motion.seq }}: {{ motion.text }}<br>
        </template>
      </div>

    </section>

    <section class="db-margins-m db-flex-row db-flex-item-7">
      <printable-team-scores :dt="ballot.debateTeams[0]" :round-info="roundInfo"></printable-team-scores>
      <div class="db-item-gutter"></div>
      <printable-team-scores :dt="ballot.debateTeams[1]" :round-info="roundInfo"></printable-team-scores>
    </section>
    <section class="db-margins-m db-flex-row db-flex-item-7" v-if="roundInfo.isBP">
      <printable-team-scores :dt="ballot.debateTeams[2]" :round-info="roundInfo"></printable-team-scores>
      <div class="db-item-gutter"></div>
      <printable-team-scores :dt="ballot.debateTeams[3]" :round-info="roundInfo"></printable-team-scores>
    </section>

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="!roundInfo.isBP">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row"><!-- Aff holder -->
        <div class="db-flex-item db-align-vertical-center db-flex-static db-vertical-center-text">
          Which team won the debate:
        </div>
        <div class="db-flex-item db-fill-in">
        </div>
      </div>
      <div class="db-item-gutter"></div>
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row"><!-- Aff holder -->
        <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
          By how many points did they win:
        </div>
        <div class="db-flex-item db-fill-in">
        </div>
      </div>
    </section>

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="roundInfo.showInfo">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row"><!-- Aff holder -->
        <div class="db-flex-item db-align-vertical-center db-flex-static db-vertical-center-text">
          {{ roundInfo.infoText }}
        </div>
      </div>
    </section>

  </div>
</template>

<script>
import PrintableTeamScores from './PrintableTeamScores.vue'
import _ from 'lodash'

export default {
  props: ['ballot', 'roundInfo'],
  components: {PrintableTeamScores},
  computed: {
    panellistsExcludingSelf: function() {
      var ballotSource = this.ballot.author
      var authoringPanellist = _.find(this.ballot.debateAdjudicators, function(panellist) {
        return panellist.adjudicator.name === ballotSource
      });
      if (!_.isUndefined(authoringPanellist)) {
        return _.without(this.ballot.debateAdjudicators, authoringPanellist)
      } else {
        return this.ballot.debateAdjudicators
      }
    },
    motionsAccountingForBlanks: function() {
      if (this.roundInfo.motions.length > 0) {
        return this.roundInfo.motions
      } else {
        return [{'seq': 1}, {'seq': 2}, {'seq': 3}]
      }
    }
  }
}
</script>
