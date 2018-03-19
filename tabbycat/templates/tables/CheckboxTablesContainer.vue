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
          <button class="btn btn-secondary" v-if="categories.length > 1">
            {{ bc.name }}
          </button>
          <button @click="massSelect(true, bc.id)" class="btn btn-primary">
            <i data-feather="check-circle"></i> Set All
          </button>
          <button @click="massSelect(false, bc.id)" class="btn btn-primary">
            <i data-feather="x-circle"></i> Set None
          </button>
        </div>

        <template v-if="roundInfo">
          <!-- Extensions just for availabilities -->
          <form v-if="roundInfo.break === 'True' && roundInfo.model === 'participants.Adjudicator'"
                :action="urls.breakingAdjs" method="post">
            <button class="btn btn-primary" type="submit">
              {{ gettext("Set All Breaking as Available") }}
            </button>
          </form>
          <div class="btn-group">
            <button v-if="roundInfo.prev" @click="copyFromPrevious"
                    class="btn btn-primary" type="button" data-toggle="tooltip"
                    :title="gettext('Set all the availabilities to exactly match what they were in the previous round.')">
              <i data-feather="repeat"></i> {{ gettext("Match") }} {{ roundInfo.prev }}
            </button>
            <button @click="setFromCheckIns(true)"
                    class="btn btn-primary" type="button" data-toggle="tooltip"
                    :title="gettext('Set all availabilities to exactly match check-ins.')">
              <i data-feather="repeat"></i> {{ gettext("Match Check-Ins") }}
            </button>
            <button @click="setFromCheckIns(false)"
                    class="btn btn-primary" type="button" data-toggle="tooltip"
                    :title="gettext('Set people as available only if they have a check-in and are currently unavailable — i.e. it will not overwrite any existing availabilities.')">
              <i data-feather="corner-up-right"></i> {{ gettext("Copy Check-Ins") }}
            </button>
          </div>
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
      var message = "Checks for " + payload.id + " as " + payload.checked
      this.ajaxSave(this.urls.save, payload, message, null, null, null)
    },
    toggleChecked: function(id, checked, type) {
      this.saveChecks(type)
    },
    copyFromPrevious: function() {
      _.forEach(this.tablesData[0].data, function(row) {
        row[0].checked = row[0].prev
      })
      this.saveChecks(0)
    },
    setFromCheckIns: function(match) {
      _.forEach(this.tablesData[0].data, function(row) {
        if (match) {
          row[0].checked = row[0].checked_in
        } else {
          // Only update for those checked (i.e. don't overrwrite existing)
          if (row[0].checked_in) {
            row[0].checked = row[0].checked_in
          }
        }
      })
      this.saveChecks(0)
    },
    massSelect: function(state, type) {
      _.forEach(this.tablesData[0].data, function(row) {
        _.forEach(row, function(column) {
          if (column.type === type) {
            column.checked = state
          }
        })
      })
      this.saveChecks(type)
    },
  }
}

</script>