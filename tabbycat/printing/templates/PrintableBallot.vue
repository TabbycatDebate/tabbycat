<template>
  <section class="db-score-sheet db-flex-item db-flex-column">

    <printable-ballot-header
      :ballot="ballot" :round-info="roundInfo"></printable-ballot-header>

    <printable-scoresheet v-if="kind === 'Scoresheet'"
      :ballot="ballot" :round-info="roundInfo"></printable-scoresheet>

    <printable-feedback v-if="kind === 'Feedback'"
      :ballot="ballot" :round-info="roundInfo"></printable-feedback>

    <printable-ballot-footer v-if="roundInfo.showTabRoomRow"
      :return-location="roundInfo.returnLocation"></printable-ballot-footer>

  </section>
</template>

<script>
import PrintableBallotHeader from './PrintableBallotHeader.vue'
import PrintableBallotFooter from './PrintableBallotFooter.vue'
import PrintableFeedback from './PrintableFeedback.vue'
import PrintableScoresheet from './PrintableScoresheet.vue'

export default {
  props: ['ballot', 'motions', 'positions', 'kind', 'roundInfo'],
  components: {
    PrintableBallotHeader, PrintableBallotFooter,
    PrintableFeedback, PrintableScoresheet
  },
}
</script>
