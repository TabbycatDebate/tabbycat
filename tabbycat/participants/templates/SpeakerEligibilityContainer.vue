<template>
  <div>

    <div class="row">
      <div class="col d-flex justify-content-between mb-4">

        <div class="btn-group btn-group">
          <a class="btn btn-outline-primary" :href="urls.list">
            Participants List
          </a>
          <a class="btn btn-outline-primary" :href="urls.categories">
            Speaker Categories
          </a>
          <a class="btn btn-outline-primary active" :href="urls.eligibility">
            Speaker Eligibility
          </a>
        </div>

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
  data: function () { return { rejectSave: false } },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('toggle-checked', this.toggleEligiblity)
  },
  computed: {
    eligibilties: function() {
      var eligibilties = {}
      // Map Eligibilties in table to a dictionary keyed by id
      _.forEach(this.tablesData[0].data, function(row) {
        // TODO hardcoded per row
        eligibilties[row[0].id] = {'type': row[0].type, 'checked': row[0].checked};
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
      this.rejectSave = true
      _.forEach(this.tablesData[0].data, function(row) {
        // TODO: don't key off index (can show/hide institutions column)
        row[2 + index].checked = state
      })
      this.saveEligibilties()
      this.$nextTick(function() {
        this.rejectSave = false
      })
    },
  }
}

</script>