<template>
  <div class="db-flex-row db-margins-m">

    <div class="db-flex-item db-flex-column">

      <section class="db-bordered mb-3 db-flex-row  db-flex-item-1 py-2"
               v-if="ballot.debateAdjudicators && ballot.debateAdjudicators.length > 1">
        <div class="db-padding-horizontal db-align-vertical-center db-vertical-center-text">
          <div>
            Joined by
            <span v-for="(da, i) in panellistsExcludingSelf">
              <span v-if="i !== 0">&amp;</span>
              <strong>{{ da.adjudicator.name }}</strong>
              <span v-if="da.position === 'c'">
                <small>(Chair, {{ getAdjudicatorInstitution(da) }})</small>
              </span>
              <span v-if="da.position === 'o'">
                <small>(Solo Chair, {{ getAdjudicatorInstitution(da) }})</small>
              </span>
              <span v-if="da.position === 'p'">
                <small>(Panellist, {{ getAdjudicatorInstitution(da) }})</small>
              </span>
              <span v-if="da.position === 't'">
                <small>(Trainee, {{ getAdjudicatorInstitution(da) }})</small>
              </span>
            </span>

          </div>
        </div>
      </section>

      <!-- No choice -->
      <section v-if="!roundInfo.hasMotions && roundInfo.motions.length > 0"
               class="db-bordered db-flex-row db-flex-item-1 py-2">
        <div class="db-padding-horizontal db-align-vertical-center db-vertical-center-text">
          <span>The motion is <em>{{ roundInfo.motions[0].text }}.</em></span>
        </div>
      </section>

      <!-- Choice but no motions have been entered -->
      <section v-if="roundInfo.hasMotions && !roundInfo.hasVetoes"
               class="db-bordered db-flex-row db-flex-item-1 py-2">
        <div class="db-padding-horizontal db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
          Motion:
        </div>
        <div class="db-flex-item db-align-vertical-center" v-if="roundInfo.motions.length > 0">
          <em>{{ roundInfo.motions[0].text }}</em>
        </div>
        <div v-else class="db-flex-item db-padding-horizontal db-fill-in"></div>
      </section>

      <!-- Choice and vetoes -->
      <section v-if="roundInfo.hasMotions && roundInfo.hasVetoes"
               class="db-bordered db-flex-row db-flex-item-2 py-2">

        <template v-for="choice_type in ['Selected', 'Aff Veto', 'Neg Veto']">
          <div class="db-flex-item-1 db-flex-column">
            <div class="db-flex-item-2 db-align-horizontal-center db-align-vertical-end" v-html="choice_type"></div>
            <div class="db-flex-item-1 "></div>
            <div class="db-flex-item-2 db-flex-row">
              <div v-for="motion in motionsAccountingForBlanks"
                   class="db-align-horizontal-center db-align-vertical-start db-flex-item-1 db-center-text">
                <span class="db-fill-in"><strong>{{ motion.seq }}</strong></span>
              </div>
            </div>
          </div>
          <div class="db-item-gutter"></div>
        </template>

        <div class="db-flex-item-6 db-flex-column">
          <div class="db-flex-item db-align-vertical-center py-1"
               v-for="(motion, index) in roundInfo.motions">
            <div><strong>{{ motion.seq }}</strong>: {{ motion.text }}</div>
          </div>
        </div>

      </section>

    </div>

    <template v-if="ballot.authorPosition === 'c' || ballot.authorPosition === 'o'">

      <div class="db-item-gutter"></div>

      <div class="db-flex-static db-bordered">
        <img :id="ballot.barcode" class="barcode-placeholder">
      </div>

    </template>

  </div>
</template>

<script>
import PrintableTeamScores from './PrintableTeamScores.vue'

import JsBarcode from 'jsbarcode'
import _ from 'lodash'

export default {
  props: ['ballot', 'roundInfo'],
  components: {PrintableTeamScores},
  methods: {
    getAdjudicatorInstitution: function(debateAdjudicator) {
      var institution = debateAdjudicator.adjudicator.institution
      if (!_.isUndefined(institution) && institution !== null) {
        return institution.code
      } else {
        return "Unaffiliated"
      }
    },
  },
  mounted: function() {
    var height = 65
    if (this.roundInfo.hasMotions && this.roundInfo.hasVetoes) {
      height = 85 // Blow out the height to the big veto box has space
    }
    $(".barcode-placeholder").each(function() {
      var code = $(this).attr("id")
      $(this).JsBarcode(code, {
        width: 3,
        height: height,
        text: code,
        fontSize: 16,
        textPosition: 'top',
        textMargin: 3,
        textAlign: 'right',
      })
    })
  },
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
