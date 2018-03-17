<template>

  <div>

    <div class="d-lg-flex justify-content-lg-between mb-3">

      <div class="btn-group mb-md-0 mb-3">
        <button v-for="(optionState, optionKey) in this.filterByPresence" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('filterByPresence', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>

      <div class="btn-group mb-md-0 mb-3" v-if="!isForVenues">
        <button v-for="(optionState, optionKey) in this.filterByType" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('filterByType', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>

      <div class="btn-group mb-md-0 mb-3">
        <button v-for="(optionState, optionKey) in this.sortByGroup" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('sortByGroup', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>

    </div>

    <div class="alert alert-info" v-if="entitiesByPresence.length === 0">
      No matching <span v-if="isForVenues">venues</span><span v-else>people</span> found.
    </div>
    <div class="alert alert-info">
      This page will live-update with new check-ins.
    </div>

    <transition-group :name="mainTransitions" tag="div">
      <div v-for="(entity, grouper) in entitiesBySortingSetting"
           :key="grouper" class="card mt-3">

        <div class="card-header px-2 py-1">
          <div class="row">
            <div class="col h5 mb-0 py-2">{{ grouper }}</div>
            <div class="col-auto" v-if="scanUrl">
              <button class="btn btn-info btn-sm mt-1 hoverable"
                      @click="checkInEntity(entity)">
                Check-In All <strong>✓</strong>
              </button>
            </div>
          </div>
        </div>

        <div class="card-body pl-2 pt-2 p-0">
          <transition-group :name="mainTransitions" tag="div" class="row no-gutters">

            <div v-for="entity in entity":key="entity.id"
                 class="col-lg-3 col-md-4 col-6 check-in-person">
              <div class="row no-gutters h6 mb-0 pb-2 pr-2 p-0 text-white">

                <div :class="['col p-2', entity.status ? 'bg-success' : 'bg-secondary']"
                     data-toggle="tooltip" :title="getToolTipForEntity(entity)">
                  {{ entity.name }}
                </div>
                <a v-if="scanUrl && !entity.status && entity.identifier"
                   class="col-auto p-2 btn-info text-center hoverable"
                   title="Click to check-in manually"
                   @click="checkInIdentifiers([entity.identifier])">
                  ✓
                </a>
                <div v-if="scanUrl && !entity.identifier"
                     class="col-auto p-2 btn-secondary text-white text-center"
                     data-toggle="tooltip"
                     title="This person does not have a check-in identifier so can't be checked in">
                  ?
                </div>
                <div v-if="entity.status" class="col-auto p-2 btn-success text-center">
                  {{ lastSeenTime(entity.status.time) }}
                </div>

              </div>
            </div>

          </transition-group>
        </div>

      </div>
    </transition-group>

  </div>

</template>

<script>
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'
import WebSocketMixin from '../../templates/ajax/WebSocketMixin.vue'

import PeopleStatusMixin from './PeopleStatusMixin.vue'
import VenuesStatusMixin from './VenuesStatusMixin.vue'

import _ from 'lodash'

export default {
  mixins: [AjaxMixin, WebSocketMixin, PeopleStatusMixin, VenuesStatusMixin],
  data: function() {
    return {
      filterByPresence: {
        'Absent': false, 'Present': false, 'All': true
      },
      enableAnimations: true,
      sockets: ['checkins']
    }
  },
  props: {
    'events': Array,
    'scanUrl': String,
  },
  computed: {
    isForVenues: function() {
      return this.venues === null ? false : true
    },
    filterByType: function() {
      return this.isForVenues ? this.venuesFilterByType : this.peopleFilterByType
    },
    sortByGroup: function() {
      return this.isForVenues ? this.venuesSortByGroup : this.peopleSortByGroup
    },
    mainTransitions: function() {
      // Don't want the entire list to animate when changing filter effects
      if (this.enableAnimations) {
        return 'animated-list'
      } else {
        return ''
      }
    },
    entitiesByType: function() {
      return this.isForVenues ? this.venuesByType : this.peopleByType
    },
    entitiesByPresence: function() {
      // Filter by status
      if (this.filterByPresence["All"]) {
        return this.entitiesByType
      } else {
        var filterByStatus = this.filterByPresence["Absent"]
        return _.filter(this.entitiesByType, function(p) {
          return _.isUndefined(p["status"]) === filterByStatus
        })
      }
    },
    entitiesSortedByName: function() {
      return _.sortBy(this.entitiesByPresence, ['name'])
    },
    entitiesByName: function() {
      return _.groupBy(this.entitiesSortedByName, function(p) {
        return p.name[0]
      })
    },
    entitiesByTime: function() {
      var sortedByTime = _.sortBy(this.entitiesSortedByName, function(p) {
        if (_.isUndefined(p["status"])) {
          return "Thu, 01 Jan 2070 00:00:00 GMT-0400"
        } else {
          return p.status.time
        }
      })
      var self = this
      return _.groupBy(sortedByTime, function(p) {
        if (_.isUndefined(p["status"])) {
          return "Not Checked In"
        } else {
          var time = new Date(Date.parse(p.status.time))
          var hours = self.clock(time.getHours())
          if (time.getMinutes() < 30) {
            return hours + ":00" + " - " + hours + ":29"
          } else {
            return hours + ":30" + " - " + hours + ":59"
          }
        }
      })
    },
    entitiesBySortingSetting: function() {
      if (this.sortByGroup['By Category'] === true) {
        return this.venuesByCategory
      } else if (this.sortByGroup['By Priority'] === true) {
        return this.venuesByPriority
      } else if (this.sortByGroup['By Name'] === true) {
        return this.entitiesByName
      } else if(this.sortByGroup['By Institution'] === true) {
        return this.peopleByInstitution
      } else if(this.sortByGroup['By Time'] === true) {
        return this.entitiesByTime
      }
    },
  },
  methods: {
    clock: function(timeRead) {
      var paddedTime = ("0" + timeRead).slice(-2)
      return paddedTime
    },
    checkInEntity: function(entity) {
      var identifiersForEntities = _.map(entity, 'identifier')
      this.checkInIdentifiers(identifiersForEntities)
    },
    lastSeenTime: function(timeString) {
      var time = new Date(Date.parse(timeString))
      return this.clock(time.getHours()) + ":" + this.clock(time.getMinutes())
    },
    getToolTipForEntity: function(entity) {
      return this.isForVenues ? this.getToolTipForVenue(entity) : this.getToolTipForPerson(entity)
    },
    checkInIdentifiers: function(barcodeIdentifiers) {
      var message = 'the checkin status of ' + barcodeIdentifiers
      var payload = { 'barcodes': barcodeIdentifiers }
      this.ajaxSave(this.scanUrl, payload, message, null, this.failCheckIn, null, false)
    },
    failCheckIn: function(payload, returnPayload) {
      var message = 'Failed to check in one or more identifiers: ' + payload.barcodes
      $.fn.showAlert("danger", message, 0)
    },
    setListContext: function(metaKey, selectedKey, selectedValue) {
      this.enableAnimations = false
      var self = this
      _.forEach(this[metaKey], function(value, key) {
        if (key === selectedKey) {
          self[metaKey][key] = selectedValue
        } else {
          self[metaKey][key] = false
        }
      })
      this.$nextTick(function() {
        self.enableAnimations = true
      })
    },
    handleSocketMessage: function(payload, socketLabel) {
      console.log('handleSocketMessage', socketLabel, ' : ', payload)
      this.events.push(payload)
    }
  }
}
</script>
