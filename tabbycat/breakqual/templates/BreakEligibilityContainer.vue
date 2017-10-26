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
  data: function () { return { rejectSave: false } },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('toggle-checked', this.toggleEligibilty)
  },
  computed: {
    eligibilties: function() {
      var eligibilties = {}
      _.forEach(this.categories, function(category) {
        eligibilties[category.id] = {}
      })
      // Map Eligibilties in table to a dictionary keyed by id
      _.forEach(this.tablesData[0].data, function(row) {
        _.forEach(row, function(column) {
          if (!_.isUndefined(column.type)) {
            var break_data = {'type': column.type, 'checked': column.checked }
            eligibilties[column.type][column.id] = break_data;
          }
        })
      })
      return eligibilties
    },
  },
  methods: {
    saveEligibilties: function(type) {
      var payload = this.eligibilties[type]
      var message = "Eligibilties as" + payload
      this.ajaxSave(this.urls.save, payload, message, null, null, null)
    },
    toggleEligibilty: function(id, checked, type) {
      if (this.rejectSave === false) {
        // We don't want massSelects to trigger individual updates; so just
        // pass on saving those updates
        this.saveEligibilties(type)
      }
    },
    massSelect: function(state, type) {
      this.rejectSave = true
      _.forEach(this.tablesData[0].data, function(row) {
        _.forEach(row, function(column) {
          if (column.type === type) {
            column.checked = state
          }
        })
      })
      this.saveEligibilties(type)
      this.$nextTick(function() {
        this.rejectSave = false
      })
    },
  }
}

</script>