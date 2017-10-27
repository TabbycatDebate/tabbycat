<template>
  <div>

    <div class="row">
      <div class="col d-flex justify-content-between mb-4">

        <div class="btn-group">
          <a :href="item.url" class="btn btn-outline-primary" v-for="item in navigation">
            <i data-feather="chevron-left" v-if="item.back"></i>{{ item.title }}
          </a>
        </div>

        <div class="btn-group" v-for="(bc, index) in categories">
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

        <template v-if="roundInfo">
          <!-- Extensions just for availabilities -->
          <form v-if="roundInfo.break === 'True' && roundInfo.model === 'participants.Adjudicator'"
                :action="urls.breakingAdjs" method="post">
            <button class="btn btn-primary" type="submit">
              {{ translations["Check In All Breaking"] }}
            </button>
          </form>
          <button v-if="roundInfo.seq > 1" @click="copyFromPrevious"
                  class="btn btn-primary" type="button">
            {{ translations["Copy from Previous"] }}
          </button>
        </template>

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
import AutoSaveCounter from '../draganddrops/AutoSaveCounter.vue'
import TablesContainer from './TablesContainer.vue'
import AjaxMixin from '../ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  components: { AutoSaveCounter, TablesContainer },
  props: { tablesData: Array, categories: Array, urls: Object,
           navigation: Array, roundInfo: Object, translations: Object },
  data: function () { return { rejectSave: false } },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('toggle-checked', this.toggleChecked)
  },
  computed: {
    checked: function() {
      var checked = {}
      _.forEach(this.categories, function(category) {
        checked[category.id] = {}
      })
      // Map Checks in table to a dictionary keyed by id
      _.forEach(this.tablesData[0].data, function(row) {
        _.forEach(row, function(column) {
          if (!_.isUndefined(column.type)) {
            var break_data = {'type': column.type, 'checked': column.checked }
            checked[column.type][column.id] = break_data;
          }
        })
      })
      return checked
    },
  },
  methods: {
    saveChecks: function(type) {
      var payload = this.checked[type]
      var message = "Checks as" + payload
      this.ajaxSave(this.urls.save, payload, message, null, null, null)
    },
    toggleChecked: function(id, checked, type) {
      if (this.rejectSave === false) {
        // We don't want massSelects to trigger individual updates; so just
        // pass on saving those updates
        this.saveChecks(type)
      }
    },
    copyFromPrevious: function() {
      this.rejectSave = true
      _.forEach(this.tablesData[0].data, function(row) {
        row[0].checked = row[0].prev
      })
      this.saveChecks(0)
      this.$nextTick(function() {
        this.rejectSave = false
      })
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
      this.saveChecks(type)
      this.$nextTick(function() {
        this.rejectSave = false
      })
    },
  }
}

</script>