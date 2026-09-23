<script setup>
import { computed } from 'vue'

import PrintableBallotHeader from './PrintableBallotHeader.vue'
import PrintableDebateInfo from './PrintableDebateInfo.vue'
import PrintableFeedback from './PrintableFeedback.vue'
import PrintableScoresheet from './PrintableScoresheet.vue'

const props = defineProps({
  ballot: Object,
  kind: String,
  roundInfo: Object,
  ordinals: Array,
})

const showScoring = computed(() => {
  if (props.kind === 'Scoresheet') {
    return true
  }
  return false
})
</script>

<template>
  <section class="db-score-sheet db-flex-item db-flex-column">
    <printable-ballot-header
      :ballot="ballot"
      :round-info="roundInfo"
    />

    <printable-debate-info
      :ballot="ballot"
      :round-info="roundInfo"
      :show-scoring="showScoring"
    />

    <printable-scoresheet
      v-if="kind === 'Scoresheet'"
      :ballot="ballot"
      :round-info="roundInfo"
      :ordinals="ordinals"
    />

    <printable-feedback
      v-if="kind === 'Feedback'"
      :ballot="ballot"
      :round-info="roundInfo"
    />
  </section>
</template>
