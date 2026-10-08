<script setup>
import _ from 'lodash'
import { computed } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'


const props = defineProps({
  dt: Object,
  roundInfo: Object,
  ordinals: Array,
})

const { gettext, tct } = useDjangoI18n()

const team = computed(() => {
  if (props.dt.team !== null) {
    return props.dt.team
  }
  return {
    code_name: '____________________________________________________________',
    short_name: '____________________________________________________________',
    speakers: [],
  }
})

const teamName = computed(() => {
  if (props.roundInfo.teamCodes === true) {
    return team.value.code_name
  }
  return team.value.short_name
})

const speakersList = computed(() => {
  let speakersList = ''
  _.forEach(team.value.speakers, (speaker) => {
    speakersList += `${speaker.name}, `
  })
  return speakersList.slice(0, -2)
})

const titleCasePosition = computed(() => {
  const upperWords = _.map(_.words(props.dt.side_name), word => _.upperFirst(word))
  return _.join(upperWords, ' ')
})

</script>

<template>
  <div class="db-flex-column db-bordered db-flex-item-half">
    <div class="db-flex-item-2 db-flex-row db-bottom-border">
      <div class="db-padding-horizontal flex-grow-1 db-align-vertical-center">
        <strong v-html="tct('%s, %s', [titleCasePosition, teamName])"></strong>
      </div>
      <div
        v-if="team.iron"
        class="db-padding-horizontal db-align-vertical-center strong small"
      >
        {{ gettext('IMPORTANT: Check and explicitly note if a speaker gives multiple speeches') }}
      </div>
      <div
        class="db-padding-horizontal db-align-vertical-center"
        v-html="speakersList"
      />
      <div class="db-padding-horizontal db-flex-static " />
    </div>

    <template v-for="pos in dt.positions">
      <div class="db-flex-item-3 db-flex-row db-bottom-border">
        <div
          class="db-flex-item-1 align-items-center d-flex small db-padding-horizontal"
          v-html="tct('%s:', [pos])"
        />
        <div class="db-fill-in db-flex-item-8 d-flex" />
        <div class="db-flex-item-1 align-items-center d-flex small db-padding-horizontal">
          <span>{{ gettext('Score:') }}</span>
        </div>
        <div class="db-fill-in db-flex-item-3 d-flex" />
      </div>

      <div
        v-if="roundInfo.showDigits"
        class="db-flex-item-2 align-items-center d-flex pr-1 small db-bottom-border"
      >
        <div
          class="db-flex-item-2 db-padding-horizontal text-secondary"
        >{{ tct('Circle the last digit of the %s\'s score:', [pos]) }}</div>
        <div class="db-flex-item-3 d-flex">
          <div
            v-for="(n, i) in 10"
            class="flex-fill text-center"
          >
            <span class="db-circle">{{ i }}</span>
          </div>
        </div>
      </div>
    </template>

    <div class="db-flex-item-3 db-flex-row db-bottom-border">
      <!-- Totals -->
      <template v-if="roundInfo.isBP">
        <div class="db-flex-item-2 align-items-center d-flex small db-padding-horizontal">
          {{ gettext('Circle Rank:') }}
        </div>
        <div class="db-flex-item-6 db-flex-row">
          <div
            v-for="ord in ordinals"
            class="flex-grow-1 db-align-vertical-center db-align-horizontal-center"
          >
            <span
              class="db-circle text-monospace"
              v-html="ord"
            />
          </div>
        </div>
        <div class="db-flex-item-1">
          <!-- Spacing -->
        </div>
      </template>
      <template v-else>
        <div class="db-flex-item-9 db-padding-horizontal">
          <!-- Spacing -->
        </div>
      </template>
      <div class="db-flex-item-1 align-items-center d-flex small db-padding-horizontal">
        <span>{{ gettext('Total:') }}</span>
      </div>
      <div class="db-fill-in db-flex-item-3 d-flex" />
    </div>

    <div
      v-if="roundInfo.showDigits"
      class="db-flex-item-2 align-items-center d-flex pr-1 small"
    >
      <div class="db-flex-item-2 db-padding-horizontal text-secondary">
        {{ gettext('Circle the last digit of the team\'s total:') }}
      </div>
      <div class="db-flex-item-3 d-flex">
        <div
          v-for="(n, i) in 10"
          class="flex-fill text-center"
        >
          <span class="db-circle">{{ i }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
