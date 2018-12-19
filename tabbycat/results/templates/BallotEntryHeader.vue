<template>
  <div class="card">
    <div class="list-group list-group-flush">

      <div class="list-group-item pt-4">
        <h4 class="card-title mt-0 mb-2 d-inline-block">
          <span v-if="isNew">New Ballot Set for </span>
          <span v-if="!isNew">Edit Ballot Set for </span>
          {{ debate }}
        </h4>
        <div class="badge badge-secondary float-right ml-2 mt-1">
          {{ round }}
        </div>
        <div class="badge badge-secondary float-right ml-2 mt-1">
          {{ venue }}
        </div>
      </div>
      <!-- TODO: Side choosing -->
      <!-- TODO: Motion choosing -->
      <!-- TODO: Veto choosing -->

      <div class="list-group-item pb-3 pt-3">
        <div class="form-group" v-if="!showDuplicates">
          <select class="required custom-select form-control" v-model="hasIron" @change="setIron()">
            <option value="No">
              There were no speakers who spoke multiple times (i.e. no 'Iron' person speeches)
            </option>
            <option value="Yes">
              There were speakers who spoke multiple times (i.e. one or more 'Iron' person speeches)
            </option>
          </select>
        </div>
        <div class="alert alert-info mb-0" v-if="showDuplicates">
          Speeches marked as 'duplicates' are hidden from the speaker tab and often need to be
          tracked in order to determine break eligibility. If a speaker is 'iron-manning' you would
          typically set their lowest-scoring speech as the 'duplicate'.
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  props: { debate: String, venue: String, round: String, isNew: Boolean, showDuplicates: Boolean },
  data: function () {
    return {
      hasIron: 'No',
    }
  },
  methods: {
    setIron: function () {
      if (this.hasIron === 'Yes') {
        this.$emit('set-duplicates')
      }
    },
  },
}
</script>
