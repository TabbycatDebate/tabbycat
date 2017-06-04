<template>

  <section class="db-score-sheet db-flex-item db-flex-column">

    <ballot-header :data="data" :ballot="ballot">
    </ballot-header>

    <scoresheet v-if="data.kind === 'Scoresheet'"
                :data="data" :ballot="ballot"
                :motions="motions" :positions="positions">
    </scoresheet>

    <feedback :data="data" :ballot="ballot" v-if="data.kind === 'Feedback'">
    </feedback>

    <ballot-footer v-if="data.showTabRoomRow"
                   :return-location="data.returnLocation">
    </ballot-footer>

  </section>

</template>

<script>
import PrintableBallotHeader from './PrintableBallotHeader.vue'
import PrintableBallotFooter from './PrintableBallotFooter.vue'
import PrintableFeedback from './PrintableFeedback.vue'
import PrintableScoresheet from './PrintableScoresheet.vue'

export default {
  props: ['data', 'ballot', 'motions', 'positions'],
  components: {
    PrintableBallotHeader, PrintableBallotFooter,
    PrintableFeedback, PrintableScoresheet
  },
}
</script>
