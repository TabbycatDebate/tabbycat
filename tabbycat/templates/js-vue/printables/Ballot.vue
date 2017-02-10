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
import BallotHeader from './BallotHeader.vue'
import BallotFooter from './BallotFooter.vue'
import Feedback from './Feedback.vue'
import Scoresheet from './Scoresheet.vue'

export default {
  props: ['data', 'ballot', 'motions', 'positions'],
  components: {
    BallotHeader,
    BallotFooter,
    Feedback,
    Scoresheet
  },
}
</script>
