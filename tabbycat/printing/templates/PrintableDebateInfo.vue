<template>

  <section class="db-margins-m db-flex-row">

    <div class="db-bordered db-flex-item-8 p-2 d-flex flex-column">

      <div class="d-flex flex-fill align-items-center">
        <div>

          <span v-if="ballot.debateAdjudicators && ballot.debateAdjudicators.length > 1">
            Adjudicating with
            <span v-for="(da, i) in panellistsExcludingSelf">
              <template v-if="i !== 0">&amp;</template>
              <strong>{{ da.adjudicator.name }}</strong>
              <template v-if="da.position === 'c'">(Chair, </template>
              <template v-if="da.position === 'o'">(Solo Chair, </template>
              <template v-if="da.position === 'p'">(Panellist, </template>
              <template v-if="da.position === 't'">(Trainee, </template>
              {{ getAdjudicatorInstitution(da) }})
            </span>
          </span>

          <span v-if="showScoring">
            Mark speeches
            {{ scoreDisplay(roundInfo.substantiveMin) }}
            to {{ scoreDisplay(roundInfo.substantiveMax) }};
            <strong>{{ getDisplayStep(roundInfo.substantiveStep) }}</strong>.
          </span>

          <span v-if="showScoring && roundInfo.hasReplies">
            Mark replies {{ scoreDisplay(roundInfo.replyMin) }}
            to {{ scoreDisplay(roundInfo.replyMax) }};
            <strong>{{ getDisplayStep(roundInfo.replyStep) }}</strong>.
          </span>

          <span v-if="roundInfo.returnLocation !== 'TBA'">
            Return ballots to {{ roundInfo.returnLocation }}.
          </span>

        </div>
      </div>

      <!-- No motion selection; but a motion has been entered. I.E. BP/Joynt -->
      <div v-if="!roundInfo.hasMotions && roundInfo.motions.length > 0"
           class="db-flex-item-1 pt-2">
        The motion is <em>{{ roundInfo.motions[0].text }}.</em>
      </div>

      <!-- Has motion selection; but no motions entered. I.E. Australs -->
      <div v-if="roundInfo.hasMotions && !roundInfo.hasVetoes"
           class="db-flex-item-1 pt-2">
        <div class="db-flex-item db-align-vertical-center" v-if="roundInfo.motions.length > 0">
          The motion is <em>{{ roundInfo.motions[0].text }}</em>
        </div>
        <div v-else class="db-flex-item db-fill-in pt-3">
          Motion is:
        </div>
      </div>

      <!-- Has motion selection and vetoes. I.E. Australs -->
      <div v-if="roundInfo.hasMotions && roundInfo.hasVetoes"
           class="flex-fill pt-2 d-flex flex-row">
        <template v-for="choice_type in ['Aff Veto', 'Neg Veto', 'Debated', ]">
          <div class="d-flex flex-column justify-content-end">
            <div class="text-center pb-2">Circle {{ choice_type }}</div>
            <div class="d-flex text-monospace">
              <div v-for="motion in motionsAccountingForBlanks"
                   class="db-align-horizontal-center db-align-vertical-start db-flex-item-1 db-center-text m-1">
                <span class="db-circle">{{ motion.seq }}</span>
              </div>
            </div>
          </div>
          <div class="db-item-gutter"></div>
        </template>
        <div class="flex-fill">
          <div class="db-flex-item db-align-vertical-center"
               v-for="(motion, index) in roundInfo.motions">
            <div><strong>{{ motion.seq }}</strong>: {{ motion.text }}</div>
          </div>
          <div v-if="roundInfo.motions.length === 0" class="d-flex">
            <div class="flex-fill db-fill-in strong mr-3 pt-3 mt-2"
                 v-for="choice_type in ['1', '2', '3', ]">
              {{ choice_type }}:
            </div>
          </div>
        </div>
      </div>


    </div>

    <template v-if="ballot.authorPosition === 'c' || ballot.authorPosition === 'o'">
      <div class="db-item-gutter"></div>
      <div class="db-flex-static d-flex align-content-center">
        <img :id="ballot.barcode" class="barcode-placeholder">
      </div>
    </template>

    <div class="db-item-gutter"></div>
    <div class="db-bordered d-flex db-flex-item-2 text-center small">
      <div class="d-flex db-flex-item-1 flex-column p-2">
        <div class="flex-fill db-fill-in mb-1 pt-3"></div>
        <div>tab entry</div>
      </div>
      <div class="d-flex db-flex-item-1 flex-column p-2">
        <div class="flex-fill db-fill-in mb-1 pt-4"></div>
        <div>tab check</div>
      </div>
    </div>


  </section>

</template>

<script>
import _ from 'lodash'
import JsBarcode from 'jsbarcode'

import PrintableTeamScores from './PrintableTeamScores.vue'

export default {
  props: ['ballot', 'roundInfo', 'showScoring'],
  components: { PrintableTeamScores },
  methods: {
    getAdjudicatorInstitution: function (debateAdjudicator) {
      var institution = debateAdjudicator.adjudicator.institution
      if (!_.isUndefined(institution) && institution !== null) {
        return institution.code
      }
      return 'Unaffiliated'
    },
    scoreDisplay: function (number) {
      if (number % 1 === 0) {
        return Math.round(number)
      } else {
        return number
      }
    },
    getDisplayStep: function (number) {
      if (number % 1 === 0) {
        return "no ½ marks"
      } else if (number % 0.5 === 0) {
        return "½ marks are allowed"
      } else {
        return "decimal marks are allowed"
      }
    }
  },
  computed: {
    panellistsExcludingSelf: function () {
      var ballotSource = this.ballot.author
      var authoringPanellist = _.find(this.ballot.debateAdjudicators, function (panellist) {
        return panellist.adjudicator.name === ballotSource
      });
      if (!_.isUndefined(authoringPanellist)) {
        return _.without(this.ballot.debateAdjudicators, authoringPanellist)
      }
      return this.ballot.debateAdjudicators
    },
    motionsAccountingForBlanks: function () {
      if (this.roundInfo.motions.length > 0) {
        return this.roundInfo.motions
      }
      return [{ seq: 1 }, { seq: 2 }, { seq: 3 }]
    },
  },
  mounted: function () {
    var height = 60
    if (this.roundInfo.hasMotions && this.roundInfo.hasVetoes) {
      height = 85 // Blow out the height to the big veto box has space
    }
    $(".barcode-placeholder").each(function () {
      var code = $(this).attr('id')
      $(this).JsBarcode(code, {
        width: 2.5,
        height: height,
        text: code,
        displayValue: false,
        margin: 0,
      })
    })
  },
}
</script>
