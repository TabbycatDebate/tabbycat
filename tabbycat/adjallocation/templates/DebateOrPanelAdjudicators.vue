<template>

  <div class="d-flex flex-36 flex-truncate vue-droppable vue-droppable-parent">
    <draggable-allocation
      :handle-debate-or-panel-drop="handleDebateOrPanelDrop"
      :handle-panel-swap="handlePanelSwap"
      :debate-or-panel="debateOrPanel"
      :average-score="averageScore"
      :average-voting-score="averageVotingScore"
    ></draggable-allocation>
  </div>

</template>

<script>
import { mapGetters } from 'vuex'

import DraggableAllocation from './DraggableAllocation.vue'

export default {
  components: { DraggableAllocation },
  props: ['debateOrPanel', 'handleDebateOrPanelDrop', 'handlePanelSwap'],
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
