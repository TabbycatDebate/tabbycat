<template>

  <div class="d-flex flex-36 flex-truncate vue-droppable vue-droppable-parent">
    <div class="d-flex flex-column pl-2 pr-2 justify-content-around small text-monospace">
      <div class="py-1" data-toggle="tooltip" :title="gettext('Average score of panel (excluding trainees)')">
        <span v-if="averageScore">{{ averageScore }}</span>
        <span v-else class="text-muted" v-text="gettext('N/A')"></span>
      </div>
      <div class="py-1" data-toggle="tooltip" :title="gettext('Average score of voting majority in panel')">
        <span v-if="averageVotingScore">{{ averageVotingScore }}</span>
        <span v-else class="text-muted" v-text="gettext('N/A')"></span>
      </div>
    </div>
    <draggable-allocation :handle-debate-or-panel-drop="handleDebateOrPanelDrop"
                          :debate-or-panel="debateOrPanel"></draggable-allocation>
  </div>

</template>

<script>
import { mapGetters } from 'vuex'

import DraggableAllocation from './DraggableAllocation.vue'

export default {
  components: { DraggableAllocation },
  props: ['debateOrPanel', 'handleDebateOrPanelDrop'],
  computed: {
    ...mapGetters(['allocatableItems']),
    adjudicatorScores: function () {
      let adjIds = [] // Strange logic below is to avoid mutating VueX state
      const scores = []
      if (this.debateOrPanel.adjudicators.C.length > 0) {
        adjIds.push(this.debateOrPanel.adjudicators.C[0])
      }
      adjIds = [...adjIds, ...this.debateOrPanel.adjudicators.P]
      if (adjIds.length > 0) {
        for (const adjID of adjIds) {
          if (adjID in this.allocatableItems) {
            scores.push(this.allocatableItems[adjID].score)
          }
        }
      }
      return scores.sort().reverse()
    },
    averageScore: function () {
      if (this.adjudicatorScores.length > 0) {
        return this.uiRound(this.average(this.adjudicatorScores))
      }
      return false
    },
    averageVotingScore: function () {
      if (this.adjudicatorScores.length > 1) {
        const votingMajority = Math.ceil(this.adjudicatorScores.length / 2)
        const majorityScores = this.adjudicatorScores.slice(0, votingMajority)
        return this.uiRound(this.average(majorityScores))
      }
      return false
    },
  },
  methods: {
    average: function (numbers) {
      return numbers.reduce((a, b) => a + b) / numbers.length
    },
    uiRound: function (number) {
      const fullRounded = Math.round(number * 10) / 10
      return fullRounded.toPrecision(2)
    },
  },
}
</script>
