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
          <button @click="massSelect(true, bc.id)" class="btn btn-primary" type="button">
            <i data-feather="check-circle"></i> All
          </button>
          <button @click="massSelect(false, bc.id)" class="btn btn-primary" type="button">
            <i data-feather="x-circle"></i> None
          </button>
        </div>

        <template v-if="roundInfo">
          <!-- Extensions just for availabilities -->
          <form v-if="roundInfo.break === 'True' && roundInfo.model === 'participants.Adjudicator'"
                :action="urls.breakingAdjs" method="post">
            <button class="btn btn-primary" type="submit">
              <i data-feather="star"></i> {{ gettext("Set Breaking") }}
            </button>
          </form>
          <div class="btn-group">
            <button v-if="roundInfo.prev" @click="copyFromPrevious"
                    class="btn btn-primary" type="button" data-toggle="tooltip"
                    :title="gettext(`Set all the availabilities to exactly match
                                     what they were in the previous round.`)">
              <i data-feather="repeat"></i> {{ gettext("Match") }} {{ roundInfo.prev }}
            </button>
            <button @click="setFromCheckIns(true, true)"
                    class="btn btn-primary" type="button" data-toggle="tooltip"
                    :title="gettext('Set all availabilities to exactly match check-ins.')">
              <i data-feather="repeat"></i> {{ gettext("Match Check-Ins") }}
            </button>
            <button @click="setFromCheckIns(true, false)"
                    class="btn btn-primary" type="button" data-toggle="tooltip"
                    :title="gettext(`Set people who are checked in as available
                                     (leave people not checked in unchanged)`)">
              <i data-feather="corner-up-right"></i> {{ gettext("Set from Check-Ins") }}
            </button>
            <button @click="setFromCheckIns(false, true)"
                    class="btn btn-primary" type="button" data-toggle="tooltip"
                    :title="gettext(`Set people who are not checked in as unavailable
                                     (leave people who are checked in unchanged)`)">
              <i data-feather="corner-down-left"></i> {{ gettext("Unset from Check-Ins") }}
            </button>
          </div>
        </template>

        <auto-save-counter v-if="!hideAutoSave" :css="'btn-md'"></auto-save-counter>

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
import AutoSaveCounter from '../../templates/allocations/AutoSaveCounter.vue'
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
    hideAutoSave: Boolean,
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
        row[0].sort = row[0].prev
      })
      this.saveChecks(0)
    },
    setFromCheckIns: function (set, unset) {
      _.forEach(this.tablesData[0].data, (row) => {
        if (set && row[0].checked_in) {
          row[0].checked = true
          row[0].sort = true
        } else if (unset && !row[0].checked_in) {
          row[0].checked = false
          row[0].sort = false
        }
      })
      this.saveChecks(0)
    },
    massSelect: function (state, type) {
      _.forEach(this.tablesData[0].data, (row) => {
        _.forEach(row, (column) => {
          if (column.type === type) {
            column.checked = state
            column.sort = state
          }
        })
      })
      if (!this.hideAutoSave) {
        this.saveChecks(type)
      }
    },
  },
}

</script>
