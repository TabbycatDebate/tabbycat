<template>

  <section class="db-margins-m db-flex-row">

    <div class="db-bordered db-flex-item-8 p-2 d-flex flex-column">

      <div class="d-flex flex-fill align-items-center">
        <div>

          <span v-if="ballot.debateAdjudicators && ballot.debateAdjudicators.length > 1">
            {{ panellistsAsString }}
          </span>

          <span v-if="showScoring"
                v-text="gettext('Mark speeches %1 to %2; <strong>%3</strong>.', scoreDisplay(roundInfo.substantiveMin), scoreDisplay(roundInfo.substantiveMax), getDisplayStep(roundInfo.substantiveStep))"></span>

          <span v-if="showScoring && roundInfo.hasReplies"
                v-text="gettext('Mark replies %1 to %2; <strong>%3</strong>.', scoreDisplay(roundInfo.replyMin), scoreDisplay(roundInfo.replyMax), getDisplayStep(roundInfo.replyStep))"></span>

          <span v-if="roundInfo.returnLocation !== 'TBA'"
                v-text="gettext('Return ballots to %1.', roundInfo.returnLocation)"></span>

        </div>
      </div>

      <!-- No motion selection; but a motion has been entered. I.E. BP/Joynt -->
      <div v-if="!roundInfo.hideMotions && !roundInfo.hasMotions && roundInfo.motions.length > 0"
           class="db-flex-item-1 pt-2"
           v-text="gettext('The motion is <em>%1</em>', roundInfo.motions[0].text)"></div>

      <!-- No need to worry about if there is not motion selection and no motions
           have been entered; there's no use recording/providing the motion -->

      <!-- Has motion selection; but not vetoes — no defined format -->
      <div v-if="roundInfo.hasMotions && !roundInfo.hasVetoes"
           class="db-flex-item-1 pt-2">
        <div v-if="roundInfo.motions.length > 1" class="db-flex-item db-align-vertical-center">
          <template v-for="choice_type in [gettext('Debated')]">
            <div class="d-flex flex-column justify-content-end">
              <div class="text-center pb-2" v-text="gettext('Circle %1', choice_type)"></div>
              <div class="d-flex text-monospace">
                <div v-for="motion in motionsAccountingForBlanks"
                     class="db-align-horizontal-center db-align-vertical-start
                            db-flex-item-1 db-center-text m-1">
                  <span class="db-circle">{{ motion.seq }}</span>
                </div>
              </div>
            </div>
            <div class="db-item-gutter"></div>
          </template>
          <div class="flex-fill" v-if="!roundInfo.hideMotions">
            <div class="db-flex-item db-align-vertical-center"
                 v-for="motion in roundInfo.motions">
              <div v-text="gettext('<strong>%1</strong>: %2', motion.seq, motion.text)"></div>
            </div>
          </div>
        </div>
        <div v-if="!roundInfo.hideMotions && roundInfo.motions.length === 1"
             class="db-flex-item db-align-vertical-center"
             v-text="gettext('The motion is <em>%1</em>', roundInfo.motions[0].text)">
          <!-- There shouldn't only be one motion if selection is on; but useful as fallback? -->
        </div>
        <div v-if="roundInfo.hideMotions || roundInfo.motions.length === 0"
             class="db-flex-item db-fill-in pt-3" v-text="gettext('Motion is:')"></div>
      </div>

      <!-- Has motion selection and vetoes. I.E. Australs -->
      <div v-if="roundInfo.hasMotions && roundInfo.hasVetoes"
           class="flex-fill pt-2 d-flex flex-row">
        <template v-for="choice_type in [gettext('Aff Veto'), gettext('Neg Veto'), gettext('Debated'), ]">
          <div class="d-flex flex-column justify-content-end">
            <div class="text-center pb-2" v-text="gettext('Circle %1', choice_type)"></div>
            <div class="d-flex text-monospace">
              <div v-for="motion in motionsAccountingForBlanks"
                   class="db-align-horizontal-center db-align-vertical-start
                          db-flex-item-1 db-center-text m-1">
                <span class="db-circle">{{ motion.seq }}</span>
              </div>
            </div>
          </div>
          <div class="db-item-gutter"></div>
        </template>
        <div class="flex-fill">
          <div class="db-flex-item db-align-vertical-center"
               v-for="motion in roundInfo.motions"
               v-if="!roundInfo.hideMotions">
            <div v-text="gettext('<strong>%1</strong>: %2', motion.seq, motion.text)"></div>
          </div>
          <div class="d-flex"
               v-if="roundInfo.motions.length === 0 || roundInfo.hideMotions">
            <div class="flex-fill db-fill-in strong mr-3 pt-3 mt-2"
                 v-for="choice_type in [gettext('1'), gettext('2'), gettext('3'), ]"
                 v-text="gettext('%1:', choice_type)"></div>
          </div>
        </div>
      </div>

    </div>

    <template v-if="ballot.authorPosition === 'c' || ballot.authorPosition === 'o'">
      <div class="db-item-gutter"></div>
      <div class="db-flex-static d-flex align-content-center">
        <svg :id="ballot.barcode" class="barcode-placeholder"
             :jsbarcode-value="ballot.barcode" jsbarcode-displayvalue="false"
             jsbarcode-width="2.5" jsbarcode-height="85"
             v-if="roundInfo.hasMotions && roundInfo.hasVetoes">
        </svg>
        <svg :id="ballot.barcode" class="barcode-placeholder"
             :jsbarcode-value="ballot.barcode" jsbarcode-displayvalue="false"
             jsbarcode-width="2.5" jsbarcode-height="60" v-else>
        </svg>
      </div>
    </template>

    <div class="db-item-gutter"></div>
    <div class="db-bordered d-flex db-flex-item-2 text-center small">
      <div class="d-flex db-flex-item-1 flex-column p-2">
        <div class="flex-fill db-fill-in mb-1 pt-3"></div>
        <div v-text="gettext('tab entry')"></div>
      </div>
      <div class="d-flex db-flex-item-1 flex-column p-2">
        <div class="flex-fill db-fill-in mb-1 pt-4"></div>
        <div v-text="gettext('tab check')"></div>
      </div>
    </div>

  </section>

</template>

<script>
import _ from 'lodash'

import PrintableTeamScores from './PrintableTeamScores.vue'

export default {
  props: ['ballot', 'roundInfo', 'showScoring'],
  components: { PrintableTeamScores },
  methods: {
    getAdjudicatorInstitution: function (debateAdjudicator) {
      const institution = debateAdjudicator.adjudicator.institution
      if (!_.isUndefined(institution) && institution !== null) {
        return institution.code
      }
      return this.gettext('Unaffiliated')
    },
    scoreDisplay: function (number) {
      if (number % 1 === 0) {
        return Math.round(number)
      }
      return number
    },
    getDisplayStep: function (number) {
      if (number % 1 === 0) {
        return this.gettext('no ½ marks')
      } else if (number % 0.5 === 0) {
        return this.gettext('½ marks are allowed')
      }
      return this.gettext('decimal marks are allowed')
    },
  },
  computed: {
    panellistsExcludingSelf: function () {
      const ballotSource = this.ballot.author
      const ballotAdjs = this.ballot.debateAdjudicators
      const authoringPanellist = _.find(ballotAdjs, p => p.adjudicator.name === ballotSource)
      if (!_.isUndefined(authoringPanellist)) {
        return _.without(this.ballot.debateAdjudicators, authoringPanellist)
      }
      return this.ballot.debateAdjudicators
    },
    panellistsAsString: function () {
      let adjs = []
      this.panellistsExcludingSelf.forEach((a) => {
        let position = ''
        switch (a.position) {
          case 'c':
            position = this.gettext('Chair')
            break
          case 'o':
            position = this.gettext('Solo Chair')
            break
          case 'p':
            position = this.gettext('Panellist')
            break
          case 't':
            position = this.gettext('Trainee')
            break
          default:
            break
        }
        adjs.push(this.gettext('%1 (%2, %3)', a.adjudicator.name, position, this.getAdjudicatorInstitution(a)))
      })
      return this.gettext('Adjudicating with %1.', adjs.join(this.gettext('; ')))
    },
    motionsAccountingForBlanks: function () {
      if (this.roundInfo.motions.length > 0) {
        return this.roundInfo.motions
      }
      return [{ seq: 1 }, { seq: 2 }, { seq: 3 }]
    },
  },
}
</script>
