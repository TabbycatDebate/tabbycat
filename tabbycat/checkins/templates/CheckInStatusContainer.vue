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

      <div class="btn-group mb-md-0 mb-3" v-if="!isForVenues">
        <button v-for="(optionState, optionKey) in this.speakerGroupings" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('speakerGroupings', optionKey, !optionState)">
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
      This page will live-update with new check-ins as they occur although the initial list may be up to a minute old. <template v-if="assistantUrl"> If you want to view this page without the sidebar (i.e. for displaying to an auditorium) you can <a :href="assistantUrl" target="_blank"> open the assistant version.</a></template>
    </div>

    <transition-group :name="mainTransitions" tag="div">
      <div v-for="(entity, grouper) in entitiesBySortingSetting"
           :key="grouper" class="card mt-2">

        <div class="card-header px-1 py-1">
          <div class="row">
            <div class="col strong mt-1 pt-1 ml-1">{{ grouper }}</div>
            <div class="col-auto" v-if="scanUrl">
              <button class="btn btn-info btn-sm hoverable"
                      @click="checkInGroup(entity)">
                Check-In All <strong>✓</strong>
              </button>
            </div>
          </div>
        </div>

        <div class="card-body pl-1 pt-1 p-0">
          <transition-group :name="mainTransitions" tag="div" class="row no-gutters">

            <div v-for="entity in entity":key="entity.id"
                 class="col-lg-3 col-md-3 col-6 check-in-person">
              <div class="row no-gutters h6 mb-0 pb-1 pr-1 p-0 text-white">

                <div :class="['col p-2',
                              entity.status ? 'bg-success' : 'bg-secondary',
                              entity.type === 'Adjudicator' ? 'text-capitalize' : '']"
                     data-toggle="tooltip" :title="getToolTipForEntity(entity)">
                  {{ entity.name }}
                </div>
                <a v-if="scanUrl && !entity.status && entity.identifier && !entity.locked"
                   class="col-auto p-2 btn-info text-center hoverable"
                   title="Click to check-in manually"
                   @click="checkInIdentifiers(entity.identifier)">
                  ✓
                </a>
                <div v-if="scanUrl && !entity.status && entity.identifier.length > 0 && entity.locked"
                     class="col-auto p-2 btn-secondary text-center btn-no-hover">
                  saving...
                </div>
                <div v-if="scanUrl && entity.identifier.length === 0"
                     class="col-auto p-2 btn-secondary text-white text-center"
                     data-toggle="tooltip"
                     title="This person does not have a check-in identifier so can't be checked in">
                  ?
                </div>
                <div v-if="entity.status" class="col-auto p-2 btn-success btn-no-hover text-center">
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
import FeatherMixin from '../../templates/tables/FeatherMixin.vue'
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
    'assistantUrl': String
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
      } else if (this.filterByPresence["Absent"]) {
        return _.filter(this.entitiesByType, function(p) {
          return p["status"] === false
        })
      } else {
        return _.filter(this.entitiesByType, function(p) {
          return p["status"] !== false
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
        if (_.isUndefined(p["status"]) || p["status"] === false) {
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
    checkInGroup: function(entity) {
      var identifiersForEntities = _.flatten(_.map(entity, 'identifier'))
      console.log('test', identifiersForEntities)
      this.checkInIdentifiers(identifiersForEntities)
    },
    checkInIdentifiers: function(barcodeIdentifiers) {
      var message = 'the checkin status of ' + barcodeIdentifiers
      var payload = { 'barcodes': barcodeIdentifiers }
      this.setLocked(barcodeIdentifiers, true)
      this.ajaxSave(this.scanUrl, payload, message, this.passCheckIn, this.failCheckIn, null, false)
    },
    setLocked: function(identifiers, status) {
      _.forEach(this.entitiesByType, function(entity) {
        if (_.includes(identifiers, entity.identifier)) {
          console.log('lock', entity.identifier)
          entity.locked = true
        }
      })
    },
    passCheckIn: function(dataResponse, payload, returnPayload) {
      this.setLocked(payload.barcodes, false)
    },
    failCheckIn: function(payload, returnPayload) {
      var message = 'Failed to check in one or more identifiers: ' + payload.barcodes
      $.fn.showAlert("danger", message, 0)
      this.setLocked(payload.barcodes, false)
    },
    lastSeenTime: function(timeString) {
      var time = new Date(Date.parse(timeString))
      return this.clock(time.getHours()) + ":" + this.clock(time.getMinutes())
    },
    getToolTipForEntity: function(entity) {
      return this.isForVenues ? this.getToolTipForVenue(entity) : this.getToolTipForPerson(entity)
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
