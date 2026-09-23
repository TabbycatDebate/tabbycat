<script setup>
import DraggableAllocation from './DraggableAllocation.vue'
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'

const props = defineProps(['debateOrPanel', 'handleDebateOrPanelDrop', 'handlePanelSwap'])

const store = useDragAndDropStore()
const { allocatableItems } = storeToRefs(store)

const average = (numbers) => numbers.reduce((a, b) => a + b) / numbers.length

const uiRound = (number) => {
  const fullRounded = Math.round(number * 10) / 10
  return fullRounded.toPrecision(2)
}

const adjudicatorScores = computed(() => {
  let adjIds = []
  const scores = []
  if (props.debateOrPanel.adjudicators.C.length > 0) {
    adjIds.push(props.debateOrPanel.adjudicators.C[0])
  }
  adjIds = [...adjIds, ...props.debateOrPanel.adjudicators.P]
  if (adjIds.length > 0) {
    for (const adjID of adjIds) {
      if (adjID in allocatableItems.value) {
        scores.push(allocatableItems.value[adjID].score)
      }
    }
  }
  return scores.sort().reverse()
})

const averageScore = computed(() => {
  if (adjudicatorScores.value.length > 0) {
    return uiRound(average(adjudicatorScores.value))
  }
  return false
})

const averageVotingScore = computed(() => {
  if (adjudicatorScores.value.length > 1) {
    const votingMajority = Math.ceil(adjudicatorScores.value.length / 2)
    const majorityScores = adjudicatorScores.value.slice(0, votingMajority)
    return uiRound(average(majorityScores))
  }
  return false
})
</script>

<template>
  <div class="d-flex flex-36 flex-truncate vue-droppable vue-droppable-parent">
    <draggable-allocation
      :handle-debate-or-panel-drop="handleDebateOrPanelDrop"
      :handle-panel-swap="handlePanelSwap"
      :debate-or-panel="debateOrPanel"
      :average-score="averageScore"
      :average-voting-score="averageVotingScore"
    />
  </div>
</template>
