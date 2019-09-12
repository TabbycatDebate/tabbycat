<template>
  <section class="db-score-sheet db-flex-item db-flex-column">

    <printable-ballot-header
      :ballot="ballot"
      :round-info="roundInfo"></printable-ballot-header>

    <printable-debate-info
      :ballot="ballot"
      :round-info="roundInfo"
      :show-scoring="showScoring"></printable-debate-info>

    <printable-scoresheet v-if="kind === 'Scoresheet'"
      :ballot="ballot"
      :round-info="roundInfo"
      :ordinals="ordinals"></printable-scoresheet>

    <printable-feedback v-if="kind === 'Feedback'"
      :ballot="ballot"
      :round-info="roundInfo"></printable-feedback>

  </section>
</template>

<script>
import PrintableBallotHeader from './PrintableBallotHeader.vue'
import PrintableDebateInfo from './PrintableDebateInfo.vue'
import PrintableFeedback from './PrintableFeedback.vue'
import PrintableScoresheet from './PrintableScoresheet.vue'

export default {
  props: ['ballot', 'kind', 'roundInfo', 'ordinals'],
  components: {
    PrintableBallotHeader,
    PrintableDebateInfo,
    PrintableFeedback,
    PrintableScoresheet,
  },
  computed: {
    showScoring: function () {
      if (this.kind === 'Scoresheet') {
        return true
      }
      return false
    },
  },
}
</script>
