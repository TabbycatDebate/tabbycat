<template>

  <div class="d-flex flex-36 pl-2 flex-truncate vue-droppable vue-droppable-parent">
    <div class="d-flex flex-column justify-content-around small text-monospace">
      <div class="py-1" data-toggle="tooltip" :title="gettext('Average score of panel (excluding trainees)')">
        {{ averageScore }}
      </div>
      <div class="py-1" data-toggle="tooltip" :title="gettext('Average score of voting majority in panel')">
        {{ averageVotingScore }}
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
  props: [ 'debateOrPanel', 'handleDebateOrPanelDrop' ],
  computed: {
    ...mapGetters(['allocatableItems']),
    adjudicatorScores: function () {
      let adjIds = [] // Strange logic below is to avoid mutating VueX state
      if (this.debateOrPanel.adjudicators.C.length > 0) {
        adjIds.push(this.debateOrPanel.adjudicators.C[0])
      }
      adjIds = [...adjIds, ...this.debateOrPanel.adjudicators.P]
      if (adjIds.length > 0) {
        return adjIds.map(id => this.allocatableItems[id].score).sort().reverse()
      }
      return []
    },
    averageScore: function () {
      if (this.adjudicatorScores.length > 0) {
        return this.uiRound(this.average(this.adjudicatorScores))
      }
      return 'N/A'
    },
    averageVotingScore: function () {
      if (this.adjudicatorScores.length > 1) {
        let votingMajority = Math.ceil(this.adjudicatorScores.length / 2)
        let majorityScores = this.adjudicatorScores.slice(0, votingMajority)
        return this.uiRound(this.average(majorityScores))
      }
      return 'N/A'
    },
  },
  methods: {
    average: function (numbers) {
      return numbers.reduce((a, b) => a + b) / numbers.length
    },
    uiRound: function (number) {
      let fullRounded = Math.round(number * 10) / 10
      return fullRounded.toFixed(1)
    },
  },
}
</script>
