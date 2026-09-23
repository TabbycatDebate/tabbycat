<script setup>
import _ from 'lodash'

import { computed, ref, toRef } from 'vue'
import { useWebSocket } from '../../templates/composables/useWebSocket.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'


const props = defineProps({
  initialEvents: Array,
  teamCodes: Boolean,
  tournamentSlug: String,
  forAdmin: Boolean,
  speakers: Array,
  adjudicators: Array,
  venues: Array,
  teamSize: {
    type: Number,
    default: 2,
  },
  prelimsCompleted: {
    type: Boolean,
    default: false,
  },
})

const { gettext, tct } = useDjangoI18n()

const filterByPresence = ref({ All: true, Absent: false, Present: false })
const events = ref([...(props.initialEvents ?? [])])

const showCodeNames = ref(props.teamCodes)

const peopleFilterByType = ref({ All: true, Adjudicators: false, Debaters: false, Breaking: false })
const peopleSortByGroup = ref({ Institution: !props.teamCodes, Name: props.teamCodes, Time: false })
const speakerGroupings = ref({ Speaker: false, Team: true })
const venuesSortByGroup = ref({ Category: true, Name: false, Time: false, Priority: false })

const peopleFilterNames = {
  All: 'All',
  Adjudicators: 'Only Adjudicators',
  Debaters: 'Only Teams',
  Breaking: 'Only Breaking',
}

const speakerGroupingNames = {
  Speaker: 'By Person',
  Team: 'By Team',
}

const isForVenues = computed(() => Array.isArray(props.venues))
const filterByType = computed(() => (isForVenues.value ? null : peopleFilterByType.value))
const filterByTypeOptions = computed(() => {
  const f = peopleFilterByType.value
  const options = []
  _.forEach(f, (state, key) => {
    if (key === 'Breaking' && !props.prelimsCompleted) {
      return
    }
    options.push({ key, state })
  })
  return options
})
const sortByGroup = computed(() => (isForVenues.value ? venuesSortByGroup.value : peopleSortByGroup.value))

const clock = (timeRead) => (`0${timeRead}`).slice(-2)

const annotatePeople = (list) => {
  return list.map((person) => {
    const personCopy = { ...person }
    const status = _.find(events.value, ['identifier', personCopy.identifier[0]])
    personCopy.status = status || false
    return personCopy
  })
}

// Show the toggle only when code names are the current primary display AND the payload
// includes both fields (i.e. the server confirmed the user has permission to see real names).
const canToggleNames = computed(() =>
  (props.speakers ?? []).some(s => s.team_code_name && s.team_real_name),
)

const annotatedSpeakers = computed(() => {
  const speakers = annotatePeople([...(props.speakers ?? [])])
  return speakers.map((speaker) => ({
    ...speaker,
    team: showCodeNames.value
      ? (speaker.team_code_name ?? speaker.team)
      : (speaker.team_real_name ?? speaker.team),
    institution: showCodeNames.value
      ? { code: gettext('Anonymous (due to team codes)'), name: gettext('Anon') }
      : speaker.institution,
  }))
})

const annotatedTeams = computed(() => {
  const teams = []
  const groupedSpeakers = _.groupBy(annotatedSpeakers.value, 'team')
  _.forEach(groupedSpeakers, (teamSpeakers, teamName) => {
    const institution = teamSpeakers[0].institution
    const team = {
      name: teamName,
      id: teamName,
      locked: false,
      type: 'Team',
      speakers: teamSpeakers,
      speakersIn: teamSpeakers.length - _.filter(teamSpeakers, ['status', false]).length,
      institution: institution,
      identifier: _.flatten(_.map(teamSpeakers, 'identifier')),
      breaking: _.some(teamSpeakers, speaker => speaker.breaking),
    }
    if (_.filter(team.speakers, ['status', false]).length > 0) {
      team.status = false
    } else {
      const lastCheckedIn = _.sortBy(team.speakers, [function (speaker) { return speaker.status.time }])
      team.status = { time: lastCheckedIn[0].status.time }
    }
    teams.push(team)
  })
  return teams
})

const annotatedDebaters = computed(() => {
  if (speakerGroupings.value.Speaker) {
    return annotatedSpeakers.value
  }
  return annotatedTeams.value
})

const annotatedAdjudicators = computed(() => {
  const adjs = [...(props.adjudicators ?? [])]
  return adjs.map((adjudicator) => {
    const adjCopy = { ...adjudicator }
    if (adjCopy.independent) {
      adjCopy.institution = { code: gettext('Independent'), name: gettext('Independent') }
    }
    const status = _.find(events.value, ['identifier', adjCopy.identifier[0]])
    adjCopy.status = status || false
    return adjCopy
  })
})

const peopleByType = computed(() => {
  const f = filterByType.value
  if (!f) {
    return []
  }
  const entities = []
  const includeAdjudicators = f.All || f.Adjudicators || f.Breaking
  if (includeAdjudicators) {
    _.forEach(annotatedAdjudicators.value, (adjudicator) => { entities.push(adjudicator) })
  }
  const includeDebaters = f.All || f.Debaters || f.Breaking
  if (includeDebaters) {
    _.forEach(annotatedDebaters.value, (speakerOrTeam) => { entities.push(speakerOrTeam) })
  }
  if (f.Breaking) {
    return _.filter(entities, person => person.breaking)
  }
  return entities
})

const getToolTipForPerson = (entity) => {
  if (!showCodeNames.value && entity.type !== 'Team') {
    if (entity.institution === null) {
      if (entity.identifier[0]) {
        const subs = [entity.name, entity.type, entity.identifier[0]]
        return tct('%s, a %s of no institutional affiliation with identifier of %s', subs)
      }
      const subs = [entity.name, entity.type]
      return tct('%s, a %s of no institutional affiliation with no identifier', subs)
    }
    if (entity.identifier[0]) {
      const subs = [entity.name, entity.type, entity.institution.name, entity.identifier[0]]
      return tct('%s, a %s from %s with identifier of %s', subs)
    }
    const subs = [entity.name, entity.type, entity.institution.name]
    return tct('%s, a %s from %s with no identifier', subs)
  }
  if (entity.speakers && entity.type === 'Team') {
    const speakers = []
    _.forEach(entity.speakers, (speaker) => {
      if (!speaker.identifier[0]) {
        speakers.push(tct('%s (Absent; no id)', [speaker.name]))
      } else if (speaker.status) {
        speakers.push(tct('%s (Present; id=%s)', [speaker.name, speaker.identifier[0]]))
      } else {
        speakers.push(tct('%s (Absent; id=%s)', [speaker.name, speaker.identifier[0]]))
      }
    })
    return tct('%s, a team with speakers %s', [entity.name, speakers.join(', ')])
  }
  return tct('%s, a %s', [entity.name, entity.type])
}

const entitiesByPresence = computed(() => {
  const filters = filterByPresence.value
  if (filters.All) {
    return entitiesByType.value
  } else if (filters.Absent) {
    return _.filter(entitiesByType.value, p => p.status === false)
  }
  return _.filter(entitiesByType.value, p => p.status !== false)
})

const entitiesSortedByName = computed(() => _.sortBy(entitiesByPresence.value, p => p.name.toLowerCase()))

const peopleByInstitution = computed(() => {
  const sortedByInstitution = _.sortBy(entitiesSortedByName.value, (p) => {
    if (p.institution === null) {
      return gettext('Unaffiliated')
    }
    return p.institution.code
  })
  return _.groupBy(sortedByInstitution, (p) => {
    if (p.institution === null) {
      return gettext('Unaffiliated')
    }
    return p.institution.code
  })
})

const annotatedVenues = computed(() => {
  const venues = [...(props.venues ?? [])]
  return venues.map((venue) => {
    const venueCopy = { ...venue }
    const id = Array.isArray(venueCopy.identifier) ? venueCopy.identifier[0] : null
    venueCopy.status = id ? _.find(events.value, ['identifier', id]) : false
    venueCopy.name = venueCopy.display_name
    return venueCopy
  })
})

const venuesByType = computed(() => _.forEach(annotatedVenues.value, venue => venue))

const getToolTipForVenue = (entity) => {
  const categories = []
  _.forEach(entity.categories, (c) => { categories.push(c.name) })
  if (entity.categories.length) {
    const id = Array.isArray(entity.identifier) ? entity.identifier[0] : null
    if (id) {
      const substitutions = [entity.name, categories.join(', '), id]
      return tct('%s (%s) with identifier of %s', substitutions)
    }
    const substitutions = [entity.name, categories.join(', ')]
    return tct('%s (%s) with no identifier', substitutions)
  }
  const id = Array.isArray(entity.identifier) ? entity.identifier[0] : null
  if (id) {
    const substitutions = [entity.name, id]
    return tct('%s (no category) with identifier of %s', substitutions)
  }
  return tct('%s (no category) with no identifier', [entity.name])
}

const venuesByCategory = computed(() => {
  const sortedByCategory = _.sortBy(annotatedVenues.value, (v) => {
    if (v.categories.length === 0) {
      return gettext('No Category')
    }
    return v.categories[0].name
  })
  return _.groupBy(sortedByCategory, (v) => {
    if (v.categories.length === 0) {
      return gettext('No Category')
    }
    return v.categories[0].name
  })
})

const venuesByPriority = computed(() => _.groupBy(_.sortBy(annotatedVenues.value, v => v.name.toLowerCase()), v => tct('Priority %1', [v.priority])))

const entitiesByType = computed(() => (isForVenues.value ? venuesByType.value : peopleByType.value))

const stats = computed(() => {
  return {
    Absent: _.filter(entitiesByType.value, p => p.status === false).length,
    Present: _.filter(entitiesByType.value, p => p.status !== false).length,
    All: '',
  }
})

const venuesByName = computed(() => _.groupBy(_.sortBy(annotatedVenues.value, v => v.name.toLowerCase()), p => p.name[0].toUpperCase()))

const venuesByTime = computed(() => {
  const sortedByTime = _.sortBy(_.sortBy(annotatedVenues.value, v => v.name.toLowerCase()), (p) => {
    if (_.isUndefined(p.status)) {
      return 'Thu, 01 Jan 2070 00:00:00 GMT-0400'
    }
    return p.status.time
  })
  return _.groupBy(sortedByTime, (p) => {
    const time = new Date(Date.parse(p.status.time))
    const hours = clock(time.getHours())
    if (_.isUndefined(p.status) || p.status === false) {
      return gettext('Not Checked In')
    }
    if (time.getMinutes() < 30) {
      return `${hours}:00 - ${hours}:29`
    }
    return `${hours}:30 - ${hours}:59`
  })
})

const entitiesByName = computed(() => isForVenues.value ? venuesByName.value : _.groupBy(entitiesSortedByName.value, p => p.name[0].toUpperCase()))

const entitiesByTime = computed(() => isForVenues.value ? venuesByTime.value : (() => {
  const sortedByTime = _.sortBy(entitiesSortedByName.value, (p) => {
    if (_.isUndefined(p.status)) {
      return 'Thu, 01 Jan 2070 00:00:00 GMT-0400'
    }
    return p.status.time
  })
  return _.groupBy(sortedByTime, (p) => {
    const time = new Date(Date.parse(p.status.time))
    const hours = clock(time.getHours())
    if (_.isUndefined(p.status) || p.status === false) {
      return gettext('Not Checked In')
    }
    if (time.getMinutes() < 30) {
      return `${hours}:00 - ${hours}:29`
    }
    return `${hours}:30 - ${hours}:59`
  })
})())

const entitiesBySortingSetting = computed(() => {
  if (sortByGroup.value.Category === true) {
    return venuesByCategory.value
  } else if (sortByGroup.value.Priority === true) {
    return venuesByPriority.value
  } else if (sortByGroup.value.Name === true) {
    return entitiesByName.value
  } else if (sortByGroup.value.Institution === true) {
    return peopleByInstitution.value
  } else if (sortByGroup.value.Time === true) {
    return entitiesByTime.value
  }
  return entitiesByTime.value
})

const getEntityStatusClass = (entity) => {
  let css = ''
  if (entity.type === 'Adjudicator') {
    css += 'text-capitalize '
  } else {
    css += 'text-uppercase '
  }
  if (entity.type !== 'Team' && entity.status !== false) {
    css += 'bg-success '
  } else if (entity.speakersIn >= props.teamSize && entity.speakersIn !== 0) {
    css += 'bg-success '
  } else if (props.teamSize === 2 && entity.speakersIn === 1) {
    css += 'viable-checkins-team '
  } else if (props.teamSize === 3 && entity.speakersIn === 2) {
    css += 'viable-checkins-team '
  } else if (props.teamSize === 3 && entity.speakersIn === 1) {
    css += 'not-viable-checkins-team '
  } else {
    css += 'bg-secondary '
  }
  return css
}

const lockedIdentifiers = ref(new Set())

const setLockStatus = (identifiers, status) => {
  const normalized = (Array.isArray(identifiers) ? identifiers : [identifiers])
    .flatMap((id) => {
      if (Array.isArray(id)) {
        return id
      }
      return [id]
    })
    .filter((id) => id !== null && id !== undefined)

  if (status) {
    normalized.forEach(id => lockedIdentifiers.value.add(id))
  } else {
    normalized.forEach(id => lockedIdentifiers.value.delete(id))
  }
}

const isEntityLocked = (entity) => {
  const entityId = Array.isArray(entity.identifier) ? entity.identifier[0] : entity.identifier
  return entityId && lockedIdentifiers.value.has(entityId)
}

const sockets = ['checkins']
const tournamentSlugForWSPath = toRef(props, 'tournamentSlug')

const handleSocketReceive = (_socketLabel, payload) => {
  if (payload.created === true) {
    events.value.push(...payload.checkins)
  } else {
    const revokedCheckins = payload.checkins.map(c => c.identifier)
    events.value = _.filter(events.value, event => !revokedCheckins.includes(event.identifier))
  }
  setLockStatus(payload.checkins.map(c => c.identifier), false)
}

const { sendToSocket } = useWebSocket({
  sockets,
  tournamentSlugForWSPath,
  handleSocketReceive,
})

const checkInOrOutIdentifiers = (barcodeIdentifiers, setStatus) => {
  const type = isForVenues.value ? 'venues' : 'people'
  const payload = { barcodes: barcodeIdentifiers, status: setStatus, type: type }
  setLockStatus(barcodeIdentifiers, true)
  sendToSocket('checkins', payload)
}

const checkInOrOutGroup = (entities, setStatus) => {
  const identifiersForEntities = _.flatten(_.map(entities, 'identifier'))
  const nonNullIdentifiers = _.filter(identifiersForEntities, id => id !== null)
  if (nonNullIdentifiers.length > 0) {
    checkInOrOutIdentifiers(nonNullIdentifiers, setStatus)
  }
}

const statusForGroup = (entities) => {
  return entities.every(e => e.status && e.status !== false && e.status.time !== undefined)
}

const lastSeenTime = (timeString) => {
  const time = new Date(Date.parse(timeString))
  return `${clock(time.getHours())}:${clock(time.getMinutes())}`
}

const getToolTipForEntity = (entity) => {
  if (!props.forAdmin) return null
  return isForVenues.value ? getToolTipForVenue(entity) : getToolTipForPerson(entity)
}

const setListContext = (metaKey, selectedKey, selectedValue) => {
  const state = metaKey === 'filterByPresence'
    ? filterByPresence.value
    : (metaKey === 'filterByType'
      ? peopleFilterByType.value
      : (metaKey === 'speakerGroupings'
        ? speakerGroupings.value
        : (isForVenues.value ? venuesSortByGroup.value : peopleSortByGroup.value)))
  _.forEach(state, (_value, key) => {
    if (key === selectedKey) {
      state[key] = selectedValue
    } else {
      state[key] = false
    }
  })
}

const setNameDisplay = (useCodeNames) => {
  showCodeNames.value = useCodeNames
  if (useCodeNames) {
    setListContext('sortByGroup', 'Name', true)
  } else {
    setListContext('sortByGroup', 'Institution', true)
  }
}

const forAdmin = toRef(props, 'forAdmin')
</script>

<template>
  <div>
    <div class="d-lg-flex justify-content-lg-between mb-3">
      <div class="btn-group mb-md-0 mb-3">
        <button
          v-for="(optionState, optionKey) in filterByPresence"
          :key="optionKey"
          type="button"
          :class="['btn btn-outline-primary', optionState ? 'active' : '']"
          @click="setListContext('filterByPresence', optionKey, !optionState)"
        >
          <span v-if="optionKey === 'All'">{{ gettext('All') }}</span>
          <i
            v-if="optionKey === 'Absent'"
            data-feather="x"
          />
          <i
            v-if="optionKey === 'Present'"
            data-feather="check"
          />
          {{ stats[optionKey] }}
        </button>
      </div>

      <div
        v-if="!isForVenues"
        class="btn-group mb-md-0 mb-3"
      >
        <button
          v-for="option in filterByTypeOptions"
          :key="option.key"
          type="button"
          :class="['btn btn-outline-primary', option.state ? 'active' : '']"
          @click="setListContext('filterByType', option.key, !option.state)"
        >
          {{ gettext(peopleFilterNames[option.key]) }}
        </button>
      </div>

      <div
        v-if="!isForVenues"
        class="btn-group mb-md-0 mb-3"
      >
        <button
          v-for="(optionState, optionKey) in speakerGroupings"
          :key="optionKey"
          type="button"
          :class="['btn btn-outline-primary', optionState ? 'active' : '']"
          @click="setListContext('speakerGroupings', optionKey, !optionState)"
        >
          {{ gettext(speakerGroupingNames[optionKey]) }}
        </button>
      </div>

      <div
        v-if="forAdmin && !isForVenues && canToggleNames"
        class="btn-group mb-md-0 mb-3"
      >
        <button
          type="button"
          :class="['btn btn-outline-secondary', !showCodeNames ? 'active' : '']"
          @click="setNameDisplay(false)"
        >
          {{ gettext('Real Names') }}
        </button>
        <button
          type="button"
          :class="['btn btn-outline-secondary', showCodeNames ? 'active' : '']"
          @click="setNameDisplay(true)"
        >
          {{ gettext('Code Names') }}
        </button>
      </div>

      <div class="btn-group mb-md-0 mb-3">
        <div class="btn btn-outline-primary disabled d-flex align-items-center">
          {{ gettext('Order') }}
        </div>
        <button
          v-for="(optionState, optionKey) in sortByGroup"
          :key="optionKey"
          type="button"
          :class="['btn btn-outline-primary', optionState ? 'active' : '']"
          @click="setListContext('sortByGroup', optionKey, !optionState)"
        >
          {{ optionKey }}
        </button>
      </div>
    </div>

    <div
      v-if="entitiesByPresence.length === 0 && isForVenues"
      class="alert alert-info"
    >
      {{ gettext('No matching rooms found.') }}
    </div>
    <div
      v-if="entitiesByPresence.length === 0 && !isForVenues"
      class="alert alert-info"
    >
      {{ gettext('No matching people found.') }}
    </div>
    <div class="alert alert-info">
      {{ gettext('This page will live-update with new check-ins as they occur although the initial list may be up to a minute old.') }}
    </div>

    <div
      v-for="(entities, grouper) in entitiesBySortingSetting"
      :key="entities[0].id"
      class="card mt-1"
    >
      <div class="card-body p-0">
        <div class="row no-gutters">
          <div class="col-12 col-md-3 col-lg-2 d-flex flex-nowrap align-items-center">
            <div class="mr-auto strong my-1 px-2">
              {{ grouper }}
            </div>
            <button
              v-if="forAdmin && statusForGroup(entities) === false"
              class="btn btn-info my-1 mr-1 px-2 align-self-stretch btn-sm hoverable p-1"
              @click="checkInOrOutGroup(entities, true)"
            >
              {{ gettext('✓ All') }}
            </button>
            <button
              v-if="forAdmin && statusForGroup(entities) === true"
              class="btn btn-secondary my-1 mr-1 px-2 align-self-stretch btn-sm hoverable p-1"
              @click="checkInOrOutGroup(entities, false)"
            >
              {{ gettext('☓ All') }}
            </button>
          </div>

          <div class="col-12 col-md-9 col-lg-10 pt-md-1 pl-md-0 pl-1">
            <div class="row no-gutters">
              <div
                v-for="entity in entities"
                :key="entity.id"
                class="col-lg-3 col-md-4 col-6 check-in-person"
              >
                <div class="row no-gutters h6 mb-0 pb-1 pr-1 p-0 text-white">
                  <div
                    :class="['col p-2 text-truncate ', getEntityStatusClass(entity)]"
                    data-toggle="tooltip"
                    :title="getToolTipForEntity(entity)"
                  >
                    {{ entity.name }}
                  </div>
                  <template v-if="forAdmin">
                    <a
                      v-if="!entity.status && entity.identifier[0] && !isEntityLocked(entity)"
                      class="col-auto p-2 btn-info text-center hoverable"
                      :title="gettext('Click to check-in manually')"
                      @click="checkInOrOutIdentifiers(entity.identifier, true)"
                    >
                      ✓
                    </a>
                    <div
                      v-if="!entity.status && entity.identifier[0] && isEntityLocked(entity)"
                      class="col-auto btn-secondary text-center btn-no-hover d-flex align-items-center"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 200 200"
                        style="height: 24px;"
                      ><linearGradient id="a11"><stop
                        offset="0"
                        stop-color="#fff"
                        stop-opacity="0"
                      /><stop
                        offset="1"
                        stop-color="#fff"
                      /></linearGradient><circle
                        fill="none"
                        stroke="url(#a11)"
                        stroke-width="30"
                        stroke-linecap="round"
                        stroke-dasharray="0 44 0 44 0 44 0 44 0 360"
                        cx="100"
                        cy="100"
                        r="70"
                        transform-origin="center"
                      ><animateTransform
                        type="rotate"
                        attributeName="transform"
                        calcMode="discrete"
                        dur="2"
                        values="360;324;288;252;216;180;144;108;72;36"
                        repeatCount="indefinite"
                      /></circle></svg>
                    </div>
                    <div
                      v-if="!entity.identifier[0]"
                      class="col-auto p-2 btn-secondary text-white text-center"
                      data-toggle="tooltip"
                      :title="gettext('This person does not have a check-in identifier so they can\'t be checked in')"
                    >
                      ?
                    </div>
                    <div
                      v-if="entity.status"
                      :title="gettext('Click to undo a check-in')"
                      class="col-auto p-2 btn-success hoverable text-center"
                      @click="checkInOrOutIdentifiers(entity.identifier, false)"
                    >
                      {{ lastSeenTime(entity.status.time) }}
                    </div>
                  </template>
                  <template v-if="!forAdmin">
                    <div
                      v-if="entity.status"
                      class="col-auto p-2 btn-success text-center"
                    >
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
