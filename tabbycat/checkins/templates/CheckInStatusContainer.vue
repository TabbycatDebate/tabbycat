<template>

  <div>

    <div class="d-lg-flex justify-content-lg-between mb-3">
      <div class="btn-group">
        <button v-for="(optionState, optionKey) in this.filterByPresence" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('filterByPresence', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>
      <div class="btn-group">
        <button v-for="(optionState, optionKey) in this.filterByType" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('filterByType', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>
      <div class="btn-group">
        <button v-for="(optionState, optionKey) in this.sortBy" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('sortBy', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>
    </div>

    <transition-group :name="mainTransitions" tag="div">
      <div v-for="(people, grouper) in peopleBySortingSetting"
           :key="grouper" class="card mt-3">

        <div class="card-header px-2 py-1">
          <div class="row">
            <div class="col h5 mb-0 py-2">{{ grouper }}</div>
            <div class="col-auto">
              <button class="btn-info btn-sm mt-1" @click="checkInPeople(people)">
                Check-In All <strong>✓</strong>
              </button>
            </div>
          </div>
        </div>

        <div class="card-body pl-2 pt-2 p-0">
          <transition-group :name="mainTransitions" tag="div" class="row no-gutters">

            <div v-for="person in people":key="person.id"
                 class="col-3 check-in-person">
              <div class="row no-gutters h6 mb-0 pb-2 pr-2 p-0 text-white">

                <div :class="['col p-2', person.status ? 'bg-info' : 'bg-warning']"
                     data-toggle="tooltip" :title="getToolTipForPerson(person)">
                  {{ person.name }}
                </div>
                <a v-if="!person.status && person.identifier"
                   class="col-auto p-2 btn-info text-center"
                   data-toggle="tooltip" title="Click to check-in manually"
                   @click="checkInIdentifiers([person.identifier])">
                  ✓
                </a>
                <div v-if="!person.identifier" class="col-auto p-2 btn-danger text-center"
                     data-toggle="tooltip" title="This person does not have a check-in identifier so can't be checked in">
                  ✖
                </div>
                <div v-if="person.status" class="col-auto p-2 btn-info text-center">
                  {{ lastSeenTime(person.status.time) }}
                </div>

              </div>
            </div>

          </transition-group>
        </div>

      </div>
    </transition-group>

    <div class="alert alert-info" v-if="peopleByPresence.length === 0">
      No matching people found.
    </div>

  </div>

</template>

<script>
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'
import WebSocketMixin from '../../templates/ajax/WebSocketMixin.vue'

import _ from 'lodash'

export default {
  mixins: [AjaxMixin, WebSocketMixin],
  data: function() {
    return {
      filterByPresence: {
        'Both': true, 'Missing': false, 'Present': false,
      },
      filterByType: {
        'Both': true, 'Adjudicators': false, 'Speakers': false,
      },
      sortBy: {
        'By Institution': true, 'By Name': false, 'By Time': false
      },
      enableAnimations: true,
      sockets: ['checkins']
    }
  },
  props: {
    'events': Array,
    'adjudicators': Array,
    'speakers': Array,
    'scanUrl': String,
  },
  computed: {
    mainTransitions: function() {
      // Don't want the entire list to animate when changing filter effects
      if (this.enableAnimations) {
        return 'animated-list'
      } else {
        return ''
      }
    },
    annotatedSpeakers: function() {
      var events = this.events
       _.forEach(this.speakers, function(person) {
        person["status"] = _.find(events, ['identifier', person.identifier])
      })
      return this.speakers
    },
    annotatedAdjudicators: function() {
      var events = this.events
      _.forEach(this.adjudicators, function(person) {
        person["status"] = _.find(events, ['identifier', person.identifier])
      })
      return this.adjudicators
    },
    peopleByType: function() {
      var people = []
      // Filter by speaker type
      if (this.filterByType['Both'] || this.filterByType['Adjudicators']) {
        _.forEach(this.annotatedAdjudicators, function(adjudicator) {
          people.push(adjudicator)
        })
      }
      if (this.filterByType['Both'] || this.filterByType['Speakers']) {
        _.forEach(this.annotatedSpeakers, function(speaker) {
          people.push(speaker)
        })
      }
      return people
    },
    peopleByPresence: function() {
      // Filter by status
      if (this.filterByPresence["Both"]) {
        return this.peopleByType
      } else {
        var filterByStatus = this.filterByPresence["Missing"]
        return _.filter(this.peopleByType, function(p) {
          return _.isUndefined(p["status"]) === filterByStatus
        })
      }
    },
    peopleByName: function() {
      var sortedByName = _.sortBy(this.peopleByPresence, ['name'])
      return _.groupBy(sortedByName, function(p) {
        return p.name[0]
      })
    },
    peopleByInstitution: function() {
      var sortedByName = _.sortBy(this.peopleByPresence, ['name'])
      var sortedByInstitution = _.sortBy(sortedByName, function(p) {
        if (p.institution === null) {
          return "Unaffiliated"
        } else {
          return p.institution.name
        }
      })
      return _.groupBy(sortedByInstitution, function(p) {
        if (p.institution === null) {
          return "Unaffiliated"
        } else {
          return p.institution.name
        }
      })
    },
    peopleByTime: function() {
      var sortedByName = _.sortBy(this.peopleByPresence, ['name'])
      var sortedByTime = _.sortBy(sortedByName, function(p) {
        if (_.isUndefined(p["status"])) {
          return "2999-01-01 01:01:01.00000+00:00"
        } else {
          return p.status.time
        }
      })
      var self = this
      return _.groupBy(sortedByTime, function(p) {
        if (_.isUndefined(p["status"])) {
          return "Not Checked In"
        } else {
          var time = new Date(p.status.time)
          var hours = self.clock(time.getHours())
          if (time.getMinutes() < 30) {
            return hours + ":00" + " - " + hours + ":29"
          } else {
            return hours + ":30" + " - " + hours + ":59"
          }
        }
      })
    },
    peopleBySortingSetting: function() {
      if (this.sortBy['By Name'] === true) {
        return this.peopleByName
      } else if(this.sortBy['By Institution'] === true) {
        return this.peopleByInstitution
      } else if(this.sortBy['By Time'] === true) {
        return this.peopleByTime
      }
      return this.peopleByName
    },
  },
  methods: {
    clock: function(timeRead) {
      var paddedTime = ("0" + timeRead).slice(-2)
      return paddedTime
    },
    checkInPeople: function(people) {
      var identifiersForPeople = _.map(people, 'identifier')
      this.checkInIdentifiers(identifiersForPeople)
    },
    lastSeenTime: function(timeString) {
      var time = new Date(timeString)
      return this.clock(time.getHours()) + ":" + this.clock(time.getMinutes())
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
    getToolTipForPerson: function(person) {
      var tt = person.name
      if (person.institution === null) {
        tt += ' of Unaffiliated'
      } else {
        tt += ' of ' + person.institution.name
      }
      tt += ' with identifier of ' + person.identifier
      return tt
    },
    handleSocketMessage: function(payload, socketLabel) {
      console.log('handleSocketMessage', socketLabel, ' : ', payload)
      this.events.push(payload)
    }
  }
}
</script>
