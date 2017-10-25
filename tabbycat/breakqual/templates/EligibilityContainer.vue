<template>
  <div>

    <div class="row">
      <div class="col d-flex justify-content-between mb-4">

        <a :href="urls.back" class="btn btn-outline-primary">
          <i data-feather="chevron-left"></i>Overview
        </a>

        <div class="btn-group" v-for="bc in categories">
          <button class="btn btn-secondary">
            {{ bc.name }}
          </button>
          <button @click="massSelect(true, bc.id)" class="btn btn-primary">
            <i data-feather="check-circle"></i> All
          </button>
          <button @click="massSelect(false, bc.id)" class="btn btn-primary">
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
    this.$eventHub.$on('toggle-availability', this.toggleAvailability)
  },
  computed: {
    availabilities: function() {
      var availabilities = {}
      // Map availabilities in table to a dictionary keyed by id
      _.forEach(this.tablesData[0].data, function(row) {
        availabilities[row[0].id] = row[0].available;
      })
      return availabilities
    },
    activeAvailabilities: function() {
      var actives = []
      _.forEach(this.availabilities, function(state, id) {
        if (state === true) { actives.push(id) }
      })
      return actives
    }
  },
  methods: {
    saveAvailabilities: function() {
      var payload = this.activeAvailabilities
      var message = "availabilities as" + payload
      this.ajaxSave(this.urls.save, payload, message, null, null, null)
    },
    toggleAvailability: function(id, status) {
      this.saveAvailabilities()
    },
    copyFromPrevious: function() {
      _.forEach(this.tablesData[0].data, function(row) {
        row[0].available = row[0].prev
      })
      this.saveAvailabilities()
    },
    massSelect: function(state) {
      _.forEach(this.tablesData[0].data, function(row) {
        row[0].available = state
      })
      this.saveAvailabilities()
    },
  }
}

</script>