<template>
  <div>

    <ballot-entry-header></ballot-entry-header>

    <div class="card mt-3">
      <div class="list-group list-group-flush">

        <div class="list-group-item pt-4">
          <h4 class="card-title float-left mt-0 mb-2">Scoresheet</h4>
          <div class="badge badge-secondary float-right ml-2 mt-1">
            <p class="mb-0">Panellist Deets</p>
          </div>
        </div>

        <div class="list-group-item scoresheet px-md-3 py-md-2 p-0">
          <div class="card-deck px-md-2 p-0">
            <ballot-entry-scoresheet></ballot-entry-scoresheet>
            <ballot-entry-scoresheet></ballot-entry-scoresheet>
          </div>
          <div class="card-deck px-md-2 p-0">
            <ballot-entry-scoresheet></ballot-entry-scoresheet>
            <ballot-entry-scoresheet></ballot-entry-scoresheet>
          </div>
        </div>

      </div>
    </div>

    <ballot-entry-footer></ballot-entry-footer>

  </div>
</template>

<script>
import BallotEntryHeader from './BallotEntryHeader.vue'
import BallotEntryScoresheet from './BallotEntryScoresheet.vue'
import BallotEntryFooter from './BallotEntryFooter.vue'

export default {
  mixins: [ ],
  components: { BallotEntryHeader, BallotEntryScoresheet, BallotEntryFooter },
  props: { },
  data: function () {
    return {
    }
  },
  methods: { },
}
</script>
