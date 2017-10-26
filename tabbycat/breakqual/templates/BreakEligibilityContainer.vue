<template>
  <div>

    <div class="row">
      <div class="col d-flex justify-content-between mb-4">

        <a :href="urls.back" class="btn btn-outline-primary">
          <i data-feather="chevron-left"></i>Overview
        </a>

        <div class="btn-group" v-for="(bc, index) in categories">
          <button class="btn btn-secondary">
            {{ bc.name }}
          </button>
          <button @click="massSelect(true, index)" class="btn btn-primary">
            <i data-feather="check-circle"></i> All
          </button>
          <button @click="massSelect(false, index)" class="btn btn-primary">
            <i data-feather="x-circle"></i> All
          </button>
        </div>

        <auto-save-counter :css="'btn-md'"></auto-save-counter>

      </div>
    </div>

    <div class="row">
      <div class="col">
        <tables-container :tables-data="tablesData"></tables-container>
      </div>
    </div>

  </div>
</template>

<script>
import AutoSaveCounter from '../../templates/draganddrops/AutoSaveCounter.vue'
import TablesContainer from '../../templates/tables/TablesContainer.vue'
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  components: { AutoSaveCounter, TablesContainer },
  props: { tablesData: Array, categories: Array, urls: Object },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('toggle-checked', this.toggleEligiblity)
  },
  computed: {
    eligibilties: function() {
      var eligibilties = {}
      // Map Eligibilties in table to a dictionary keyed by id
      _.forEach(this.tablesData[0].data, function(row) {
        eligibilties[row[0].id] = row[0].checked; // TODO hardcoded per row
      })
      return eligibilties
    },
  },
  methods: {
    saveEligibilties: function() {
      var payload = this.eligibilties
      var message = "Eligibilties as" + payload
      this.ajaxSave(this.urls.save, payload, message, null, null, null)
    },
    toggleEligibilty: function(id, status) {
      this.saveEligibilties()
    },
    massSelect: function(state, index) {
      _.forEach(this.tablesData[0].data, function(row) {
        // TODO: don't key off index (can show/hide institutions column)
        row[1 + index].checked = state
      })
      this.saveEligibilties()
    },
  }
}

</script>