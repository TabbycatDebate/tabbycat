<template>
  <section class="db-score-sheet db-flex-item db-flex-column">

    <printable-ballot-header :data="data" :ballot="ballot">
    </printable-ballot-header>

    <printable-scoresheet v-if="data.kind === 'Scoresheet'"
                          :data="data" :ballot="ballot"
                          :motions="motions" :positions="positions">
    </printable-scoresheet>

    <printable-feedback :data="data" :ballot="ballot"
                        v-if="data.kind === 'Feedback'">
    </printable-feedback>

    <printable-ballot-footer v-if="data.showTabRoomRow"
                             :return-location="data.returnLocation">
    </printable-ballot-footer>

  </section>
</template>

<script>
import PrintableBallotHeader from '../printables/PrintableBallotHeader.vue'
import PrintableBallotFooter from '../printables/PrintableBallotFooter.vue'
import PrintableFeedback from '../printables/PrintableFeedback.vue'
import PrintableScoresheet from '../printables/PrintableScoresheet.vue'

export default {
  props: ['ballot', 'motions', 'positions'],
  components: {
    PrintableBallotHeader, PrintableBallotFooter,
    PrintableFeedback, PrintableScoresheet
  },
}
</script>
