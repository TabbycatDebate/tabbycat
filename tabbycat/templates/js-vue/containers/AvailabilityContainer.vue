<template>
  <div>

    <div class="row">
      <div class="col d-flex justify-content-between mb-4">

        <a :href="urls.back" class="btn btn-outline-primary">
          <i data-feather="chevron-left"></i>{{ translations["Check-Ins"] }}
        </a>

        <form v-if="roundInfo.break === 'True' &&
                 roundInfo.model === 'participants.Adjudicator'"
              :action="urls.breakingAdjs" method="post">
          <button class="btn btn-primary" type="submit">
            {{ translations["Check In All Breaking"] }}
          </button>
        </form>

        <button v-if="roundInfo.seq > 1" @click="copyFromPrevious"
                class="btn btn-primary" type="button">
          {{ translations["Copy from Previous"] }}
        </button>

        <div class="btn-group">
          <button @click="massSelect(true)" class="btn btn-primary">
            {{ translations['Select All'] }}
          </button>
          <button @click="massSelect(false)" class="btn btn-primary">
            {{ translations['Select None'] }}
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
import AutoSaveCounter from '../draganddrops/AutoSaveCounter.vue'
import TablesContainer from '../../tables/TablesContainer.vue'
import AjaxMixin from '../ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  components: { AutoSaveCounter, TablesContainer },
  props: { tablesData: Array, roundInfo: Object,
           translations: Object, urls: Object },
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