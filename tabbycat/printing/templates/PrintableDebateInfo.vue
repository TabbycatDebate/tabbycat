<template>

  <section class="db-margins-m db-flex-row">

    <div class="db-bordered db-flex-item-4 p-2">

      <div class="db-flex-item">

        <span v-if="ballot.debateAdjudicators && ballot.debateAdjudicators.length > 1">
          Adjudicating with
          <span v-for="(da, i) in panellistsExcludingSelf">
            <span v-if="i !== 0">&amp;</span>
            <strong>{{ da.adjudicator.name }}</strong>
            <span v-if="da.position === 'c'">
              (Chair, {{ getAdjudicatorInstitution(da) }})
            </span>
            <span v-if="da.position === 'o'">
              (Solo Chair, {{ getAdjudicatorInstitution(da) }})
            </span>
            <span v-if="da.position === 'p'">
              (Panellist, {{ getAdjudicatorInstitution(da) }})
            </span>
            <span v-if="da.position === 't'">
              (Trainee, {{ getAdjudicatorInstitution(da) }})
            </span>
          </span>
        </span>

        <span v-if="showScoring">
          Mark speeches
          {{ getDisplayNumber(roundInfo.substantiveMin) }} to {{ getDisplayNumber(roundInfo.substantiveMax) }};
          <strong>{{ getDisplayStep(roundInfo.substantiveStep) }}</strong>.</span>
        <span v-if="showScoring && roundInfo.hasReplies">
          Mark replies
          {{ getDisplayNumber(roundInfo.replyMin) }} to {{ getDisplayNumber(roundInfo.replyMax) }};
          <strong>{{ getDisplayStep(roundInfo.replyStep) }}</strong>.</span>
        <span v-if="returnLocation !== ''">Return ballots to {{ roundInfo.returnLocation }}.</span>

      </div>

      <div class="db-flex-item-1 pt-2">

        <!-- No motion choice -->
        <div v-if="!roundInfo.hasMotions && roundInfo.motions.length > 0">
          The motion is <em>{{ roundInfo.motions[0].text }}.</em>
        </div>

        <!-- Choice but no motions have been entered -->
        <div v-if="roundInfo.hasMotions && !roundInfo.hasVetoes">
          <div class="db-padding-horizontal db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
            Motion:
          </div>
          <div class="db-flex-item db-align-vertical-center" v-if="roundInfo.motions.length > 0">
            <em>{{ roundInfo.motions[0].text }}</em>
          </div>
          <div v-else class="db-flex-item db-padding-horizontal db-fill-in"></div>
        </div>

        <!-- Choice and vetoes -->
        <div v-if="roundInfo.hasMotions && roundInfo.hasVetoes" class="d-flex flex-row">
          <template v-for="choice_type in ['Selected', 'Aff Veto', 'Neg Veto']">
            <div class="d-flex flex-column justify-content-end">
              <div class="text-center py-2" v-html="choice_type"></div>
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
    <div class="db-bordered d-flex db-flex-item-1 text-center small">
      <div class="d-flex db-flex-item-1 flex-column p-2">
        <div class="flex-fill db-fill-in mb-1"></div>
        <div>tab entry</div>
      </div>
      <div class="d-flex db-flex-item-1 flex-column p-2">
        <div class="flex-fill db-fill-in mb-1"></div>
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
    getDisplayNumber: function (number) {
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
    var height = 65
    if (this.roundInfo.hasMotions && this.roundInfo.hasVetoes) {
      height = 85 // Blow out the height to the big veto box has space
    }
    $(".barcode-placeholder").each(function () {
      var code = $(this).attr('id')
      $(this).JsBarcode(code, {
        width: 3,
        height: height,
        text: code,
        displayValue: false,
        margin: 0,
      })
    })
  },
}
</script>
