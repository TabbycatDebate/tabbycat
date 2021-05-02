<template>

  <div>

    <div class="d-lg-flex justify-content-lg-between mb-3">

      <div class="btn-group mb-md-0 mb-3">
        <button v-for="(optionState, optionKey) in this.filterByPresence"
                :key="optionKey" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('filterByPresence', optionKey, !optionState)">
          <span v-if="optionKey === 'All'" v-text="gettext('All')"></span>
          <i v-if="optionKey === 'Absent'" data-feather="x"></i>
          <i v-if="optionKey === 'Present'" data-feather="check"></i>
          {{ stats[optionKey] }}
        </button>
      </div>

      <div class="btn-group mb-md-0 mb-3" v-if="!isForVenues">
        <button v-for="(optionState, optionKey) in this.filterByType"
                :key="optionKey" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('filterByType', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>

      <div class="btn-group mb-md-0 mb-3" v-if="!isForVenues">
        <button v-for="(optionState, optionKey) in this.speakerGroupings"
                :key="optionKey" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('speakerGroupings', optionKey, !optionState)"
                v-text="gettext('By ' + optionKey)"></button>
      </div>

      <div class="btn-group mb-md-0 mb-3">
        <div class="btn btn-outline-primary disabled">Order</div>
        <button v-for="(optionState, optionKey) in this.sortByGroup"
                :key="optionKey" type="button"
                :class="['btn btn-outline-primary', optionState ? 'active' : '']"
                @click="setListContext('sortByGroup', optionKey, !optionState)">
          {{ optionKey }}
        </button>
      </div>

    </div>

    <div class="alert alert-info" v-if="entitiesByPresence.length === 0 && isForVenues"
         v-text="gettext('No matching rooms found.')"></div>
    <div class="alert alert-info" v-if="entitiesByPresence.length === 0 && !isForVenues"
         v-text="gettext('No matching people found.')"></div>
    <div class="alert alert-info"
         v-text="gettext('This page will live-update with new check-ins as they occur although the initial list may be up to a minute old.')">

      <template v-if="assistantUrl" v-text="gettext('If you want to view this page without the sidebar (i.e. for displaying to an auditorium) you can use the assistant version.')">
        <a :href="assistantUrl" target="_blank" v-text="gettext('Open the assistant version.')"></a></template>
    </div>

    <div v-for="(entities, grouper) in entitiesBySortingSetting" :key="entities[0].id" class="card mt-1">

      <div class="card-body p-0">
        <div class="row no-gutters">

          <div class="col-12 col-md-3 col-lg-2 d-flex flex-nowrap align-items-center">

            <div class="mr-auto strong my-1 px-2">
              {{ grouper }}
            </div>
            <button v-if="forAdmin && statusForGroup(entities) === false"
              @click="checkInOrOutGroup(entities, true)"
              class="btn btn-info my-1 mr-1 px-2 align-self-stretch btn-sm hoverable p-1"
              v-text="gettext('✓ All')"></button>
            <button v-if="forAdmin && statusForGroup(entities) === true"
              @click="checkInOrOutGroup(entities, false)"
              class="btn btn-secondary my-1 mr-1 px-2 align-self-stretch btn-sm hoverable p-1"
              v-text="gettext('☓ All')"></button>

          </div>

          <div class="col-12 col-md-9 col-lg-10 pt-md-1 pl-md-0 pl-1">
            <div class="row no-gutters">

              <div v-for="entity in entities" :key="entity.id"
                   class="col-lg-3 col-md-4 col-6 check-in-person">
                <div class="row no-gutters h6 mb-0 pb-1 pr-1 p-0 text-white">

                  <div :class="['col p-2 text-truncate ', getEntityStatusClass(entity)]"
                        data-toggle="tooltip" :title="getToolTipForEntity(entity)">
                    {{ entity.name }}
                  </div>
                  <template v-if="forAdmin">
                    <a v-if="!entity.status && entity.identifier[0] && !entity.locked"
                       class="col-auto p-2 btn-info text-center hoverable"
                       :title="gettext('Click to check-in manually')"
                       @click="checkInOrOutIdentifiers(entity.identifier, true)">
                      ✓
                    </a>
                    <div v-if="!entity.status && entity.identifier[0] && entity.locked"
                         class="col-auto p-2 btn-secondary text-center btn-no-hover"
                         v-text="gettext('saving...')"></div>
                    <div v-if="!entity.identifier[0]"
                         class="col-auto p-2 btn-secondary text-white text-center"
                         data-toggle="tooltip"
                         :title="gettext('This person does not have a check-in identifier so they can\'t be checked in')">
                      ?
                    </div>
                    <div v-if="entity.status" :title="gettext('Click to undo a check-in')"
                         class="col-auto p-2 btn-success hoverable text-center"
                         @click="checkInOrOutIdentifiers(entity.identifier, false)">
                      {{ lastSeenTime(entity.status.time) }}
                    </div>
                  </template>
                  <template v-if="!forAdmin">
                    <div v-if="entity.status" class="col-auto p-2 btn-success text-center">
                      {{ lastSeenTime(entity.status.time) }}
                    </div>
                  </template>

                </div>
              </div>

            </div>
          </div>

        </div>
      </div>

    </div>

  </div>

</template>

<script>
import _ from 'lodash'

import WebSocketMixin from '../../templates/ajax/WebSocketMixin.vue'
import PeopleStatusMixin from './PeopleStatusMixin.vue'
import VenuesStatusMixin from './VenuesStatusMixin.vue'

export default {
  mixins: [WebSocketMixin, PeopleStatusMixin, VenuesStatusMixin],
  data: function () {
    return {
      filterByPresence: {
        All: true, Absent: false, Present: false,
      },
      sockets: ['checkins'],
      // Keep internal copy as events needs to be mutated by the websocket
      // pushed changes and the data is never updated by the parent
      events: this.initialEvents,
    }
  },
  props: {
    initialEvents: Array,
    assistantUrl: String,
    teamCodes: Boolean,
    tournamentSlug: String,
    forAdmin: Boolean,
    teamSize: Number,
  },
  computed: {
    statsAbsent: function () {
      return 0
    },
    statsPresent: function () {
      return 0
    },
    stats: function () {
      return {
        Absent: _.filter(this.entitiesByType, p => p.status === false).length,
        Present: _.filter(this.entitiesByType, p => p.status !== false).length,
        All: '',
      }
    },
    isForVenues: function () {
      return this.venues !== null
    },
    filterByType: function () {
      return this.isForVenues ? this.venuesFilterByType : this.peopleFilterByType
    },
    sortByGroup: function () {
      return this.isForVenues ? this.venuesSortByGroup : this.peopleSortByGroup
    },
    entitiesByType: function () {
      return this.isForVenues ? this.venuesByType : this.peopleByType
    },
    entitiesByPresence: function () {
      // Filter by status
      if (this.filterByPresence.All) {
        return this.entitiesByType
      } else if (this.filterByPresence.Absent) {
        return _.filter(this.entitiesByType, p => p.status === false)
      }
      return _.filter(this.entitiesByType, p => p.status !== false)
    },
    entitiesSortedByName: function () {
      return _.sortBy(this.entitiesByPresence, p => p.name.toLowerCase())
    },
    entitiesByName: function () {
      return _.groupBy(this.entitiesSortedByName, p => p.name[0].toUpperCase())
    },
    entitiesByTime: function () {
      const sortedByTime = _.sortBy(this.entitiesSortedByName, (p) => {
        if (_.isUndefined(p.status)) {
          return 'Thu, 01 Jan 2070 00:00:00 GMT-0400'
        }
        return p.status.time
      })
      return _.groupBy(sortedByTime, (p) => {
        const time = new Date(Date.parse(p.status.time))
        const hours = this.clock(time.getHours())
        if (_.isUndefined(p.status) || p.status === false) {
          return this.gettext('Not Checked In')
        }
        if (time.getMinutes() < 30) {
          return `${hours}:00 - ${hours}:29`
        }
        return `${hours}:30 - ${hours}:59`
      })
    },
    entitiesBySortingSetting: function () {
      if (this.sortByGroup.Category === true) {
        return this.venuesByCategory
      } else if (this.sortByGroup.Priority === true) {
        return this.venuesByPriority
      } else if (this.sortByGroup.Name === true) {
        return this.entitiesByName
      } else if (this.sortByGroup.Institution === true) {
        return this.peopleByInstitution
      } else if (this.sortByGroup.Time === true) {
        return this.entitiesByTime
      }
      return this.entitiesByTime
    },
    tournamentSlugForWSPath: function () {
      return this.tournamentSlug
    },
  },
  methods: {
    clock: function (timeRead) {
      const paddedTime = (`0${timeRead}`).slice(-2)
      return paddedTime
    },
    getEntityStatusClass: function (entity) {
      let css = ''
      if (entity.type === 'Adjudicator') {
        css += 'text-capitalize '
      } else {
        css += 'text-uppercase '
      }
      if (entity.type !== 'Team' && entity.status !== false) {
        css += 'bg-success ' // For venues/adjudicators that are checked in
      } else if (entity.speakersIn >= this.teamSize && entity.speakersIn !== 0) {
        css += 'bg-success ' // All speakers checked in
      } else if (this.teamSize === 2 && entity.speakersIn === 1) {
        css += 'viable-checkins-team ' // Half present in BP (viable to debate)
      } else if (this.teamSize === 3 && entity.speakersIn === 2) {
        css += 'viable-checkins-team ' // 2/3rds present in Australs (viable to debate)
      } else if (this.teamSize === 3 && entity.speakersIn === 1) {
        css += 'not-viable-checkins-team ' // 1/3rd present in Australs (not viable to debate)
      } else {
        css += 'bg-secondary ' // Nothing checked in
      }
      return css
    },
    checkInOrOutGroup: function (entity, setStatus) {
      const identifiersForEntities = _.flatten(_.map(entity, 'identifier'))
      const nonNullIdentifiers = _.filter(identifiersForEntities, id => id !== null)
      if (nonNullIdentifiers.length > 0) {
        this.checkInOrOutIdentifiers(nonNullIdentifiers, setStatus)
      }
    },
    statusForGroup: function (entities) {
      // Check if all entites within a group are checked in
      const statuses = entities.map(e => e.status.time)
      const groupStatuses = statuses.every(time => time !== undefined)
      return groupStatuses
    },
    checkInOrOutIdentifiers: function (barcodeIdentifiers, setStatus) {
      // console.log(`Sending payload ${JSON.stringify(payload)}`)
      const type = this.isForVenues ? 'venues' : 'people'
      const payload = { barcodes: barcodeIdentifiers, status: setStatus, type: type }
      this.setLockStatus(barcodeIdentifiers, true)
      this.sendToSocket('checkins', payload)
    },
    setLockStatus: function (identifiers) {
      _.forEach(this.entitiesByType, (entity) => {
        if (_.includes(identifiers, entity.identifier)) {
          entity.locked = true
        }
      })
    },
    lastSeenTime: function (timeString) {
      const time = new Date(Date.parse(timeString))
      return `${this.clock(time.getHours())}:${this.clock(time.getMinutes())}`
    },
    getToolTipForEntity: function (entity) {
      if (!this.forAdmin) return null
      return this.isForVenues ? this.getToolTipForVenue(entity) : this.getToolTipForPerson(entity)
    },
    setListContext: function (metaKey, selectedKey, selectedValue) {
      _.forEach(this[metaKey], (value, key) => {
        if (key === selectedKey) {
          this[metaKey][key] = selectedValue
        } else {
          this[metaKey][key] = false
        }
      })
    },
    handleSocketReceive: function (socketLabel, payload) {
      // console.log(`Received payload ${JSON.stringify(payload)}`)
      if (payload.created === true) {
        this.events.push(...payload.checkins)
      } else {
        // Revoked checkins; remove all items that match the payload identifier
        const revokedCheckins = payload.checkins.map(c => c.identifier)
        this.events = _.filter(this.events, event => !revokedCheckins.includes(event.identifier))
      }
      this.setLockStatus(payload.checkins.map(c => c.identifier), false)
    },
  },
}
</script>
