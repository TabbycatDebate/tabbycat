<template>
  <div>

    <div class="row">
      <div class="col d-flex justify-content-between mb-4">

        <div class="btn-group">
          <a :href="item.url" v-for="item in navigation" :key="item.title"
             class="btn btn-outline-primary">
            <i data-feather="chevron-left" v-if="item.back"></i>{{ item.title }}
          </a>
        </div>

        <div class="btn-group" v-for="(bc, index) in categories" :key="index">
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
                    :title="gettext(`Set all the availabilities to exactly match
                                     what they were in the previous round.`)">
              <i data-feather="repeat"></i> {{ gettext("Match") }} {{ roundInfo.prev }}
            </button>
            <button @click="setFromCheckIns(true)"
                    class="btn btn-primary" type="button" data-toggle="tooltip"
                    :title="gettext('Set all availabilities to exactly match check-ins.')">
              <i data-feather="repeat"></i> {{ gettext("Match Check-Ins") }}
            </button>
            <button @click="setFromCheckIns(false)"
                    class="btn btn-primary" type="button" data-toggle="tooltip"
                    :title="gettext(`Set people as available only if they have
                                     a check-in and are currently unavailable —
                                     i.e. it will not overwrite any existing availabilities.`)">
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
import _ from 'lodash'
import AutoSaveCounter from '../draganddrops/LegacyAutoSaveCounter.vue'
import TablesContainer from './TablesContainer.vue'
import AjaxMixin from '../ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  components: { AutoSaveCounter, TablesContainer },
  props: {
    tablesData: Array,
    categories: Array,
    urls: Object,
    navigation: Array,
    roundInfo: Object,
    translations: Object,
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('toggle-checked', this.toggleChecked)
  },
  computed: {
    checked: function () {
      const checked = {}
      _.forEach(this.categories, (category) => {
        checked[category.id] = {}
      })
      // Map Checks in table to a dictionary keyed by id
      _.forEach(this.tablesData[0].data, (row) => {
        _.forEach(row, (column) => {
          if (!_.isUndefined(column.type)) {
            const breakData = { type: column.type, checked: column.checked }
            checked[column.type][column.id] = breakData
          }
        })
      })
      return checked
    },
  },
  methods: {
    saveChecks: function (type) {
      const payload = this.checked[type]
      const message = `Checks for ${payload.id} as ${payload.checked}`
      this.ajaxSave(this.urls.save, payload, message, null, null, null)
    },
    toggleChecked: function (id, checked, type) {
      this.saveChecks(type)
    },
    copyFromPrevious: function () {
      _.forEach(this.tablesData[0].data, (row) => {
        row[0].checked = row[0].prev
      })
      this.saveChecks(0)
    },
    setFromCheckIns: function (match) {
      _.forEach(this.tablesData[0].data, (row) => {
        if (match) {
          row[0].checked = row[0].checked_in
        } else if (row[0].checked_in) {
          // Only update for those checked (i.e. don't overrwrite existing)
          row[0].checked = row[0].checked_in
        }
      })
      this.saveChecks(0)
    },
    massSelect: function (state, type) {
      _.forEach(this.tablesData[0].data, (row) => {
        _.forEach(row, (column) => {
          if (column.type === type) {
            column.checked = state
          }
        })
      })
      this.saveChecks(type)
    },
  },
}

</script>
