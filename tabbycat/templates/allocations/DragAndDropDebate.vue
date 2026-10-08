<script setup>
// Provides the base template for a debate object used across all edit adjudicator screens
// Uses slots so that parent components can override them with custom components for editing the
// specific type of data they are responsible for
import { computed, toRef } from 'vue'
import { storeToRefs } from 'pinia'
import InlineTeam from '../../draw/templates/InlineTeam.vue'
import InlineAdjudicator from '../../adjallocation/templates/InlineAdjudicator.vue'
import { useDragAndDropStore } from './DragAndDropStore.js'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'


const props = defineProps({
  debateOrPanel: { type: Object, required: true },
  maxTeams: { type: Number, default: null },
})

const debateOrPanel = toRef(props, 'debateOrPanel')
const maxTeams = toRef(props, 'maxTeams')

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()
const { highlights, round } = storeToRefs(store)

const isElimination = computed(() => round.value?.stage === 'E')

const liveness = computed(() => {
  if ('liveness' in debateOrPanel.value) {
    return debateOrPanel.value.liveness
  }
  let count = 0
  if ('teams' in debateOrPanel.value && debateOrPanel.value.teams) {
    for (const keyAndEntry of Object.entries(debateOrPanel.value.teams)) {
      const team = keyAndEntry[1]
      if (team !== null && typeof team === 'object' && 'break_categories' in team) {
        for (const bc of team.break_categories) {
          const category = highlights.value?.break?.options?.[bc]
          if (category && team.points > category.fields.dead && team.points < category.fields.safe) {
            count += 1
          }
        }
      }
    }
  }
  return count
})

</script>

<template>
  <div class="d-flex border-bottom bg-white">
    <slot
      v-if="!isElimination"
      name="bracket"
    >
      <div
        v-if="debateOrPanel.bracket >= 0"
        class="flex-1-25 flex-truncate d-flex border-right"
        data-toggle="tooltip"
        :title="gettext(`The debate's bracket`)"
      >
        <div class="align-self-center flex-fill text-center">
          {{ debateOrPanel.bracket }}
        </div>
      </div>
      <div
        v-else
        class="flex-2 flex-truncate d-flex border-right"
        data-toggle="tooltip"
        :title="gettext(`The bracket range of the hypothetical debate`)"
      >
        <div class="align-self-center flex-fill text-center">
          <span v-if="debateOrPanel.bracket_min !== debateOrPanel.bracket_max">
            {{ debateOrPanel.bracket_min }}<span class="text-muted">-</span>{{ debateOrPanel.bracket_max }}
          </span>
          <span v-else>{{ debateOrPanel.bracket_min }}</span>
        </div>
      </div>
    </slot>
    <slot
      v-if="isElimination"
      name="rank"
    >
      <div
        v-if="debateOrPanel.bracket >= 0"
        class="flex-1-25 flex-truncate d-flex border-right"
        data-toggle="tooltip"
        :title="gettext(`The debate's room rank (break rank of highest-ranked team)`)"
      >
        <div class="align-self-center flex-fill text-center">
          {{ debateOrPanel.room_rank }}
        </div>
      </div>
    </slot>
    <slot
      v-if="!isElimination"
      name="liveness"
    >
      <div
        v-if="debateOrPanel.bracket >= 0"
        class="flex-1-25 flex-truncate border-right d-flex"
        data-toggle="tooltip"
        :title="gettext(`The total number of live break categories across
              all teams`)"
      >
        <div class="align-self-center flex-fill text-center">
          {{ liveness }}
        </div>
      </div>
      <div
        v-else
        class="flex-1-25 flex-truncate border-right d-flex"
        data-toggle="tooltip"
        :title="gettext(`The maximum possible number of live teams in
              the hypothetical debate for the open category`)"
      >
        <div class="align-self-center flex-fill text-center">
          {{ liveness }}
        </div>
      </div>
    </slot>
    <slot name="importance">
      <div
        class="flex-1-25 flex-truncate border-right d-flex"
        data-toggle="tooltip"
        :title="gettext(`This debate's priority`)"
      >
        <div class="align-self-center flex-fill text-center">
          {{ debateOrPanel.importance }}
        </div>
      </div>
    </slot>
    <slot name="venue">
      <div class="flex-6 flex-truncate border-right align-self-center p-2 small">
        <span v-if="debateOrPanel.venue">{{ debateOrPanel.venue.display_name }}</span>
      </div>
    </slot>
    <slot name="teams">
      <div
        v-if="debateOrPanel.teams"
        class="teams-list"
        :style="{ flex: (maxTeams + maxTeams % 2) * 3, 'flex-direction': 'row !important', 'flex-wrap': 'wrap' }"
      >
        <div
          v-for="(team, index) in debateOrPanel.teams"
          :key="team ? team.id : 'empty-' + index"
          :class="['d-flex flex-fill flex-truncate align-items-center']"
        >
          <inline-team
            v-if="team !== null"
            :debate-id="debateOrPanel.id"
            :is-elimination="isElimination"
            :team="team"
          />
        </div>
      </div>
    </slot>
    <slot name="adjudicators">
      <div class="flex-16 align-self-center p-2 small d-flex flex-wrap">
        <inline-adjudicator
          v-for="adj in debateOrPanel.adjudicators.C"
          :key="'C-' + adj.id"
          :adjudicator="adj"
          :debate-id="debateOrPanel.id"
          role="C"
        />
        <inline-adjudicator
          v-for="adj in debateOrPanel.adjudicators.P"
          :key="'P-' + adj.id"
          :adjudicator="adj"
          :debate-id="debateOrPanel.id"
          role="P"
        />
        <inline-adjudicator
          v-for="adj in debateOrPanel.adjudicators.T"
          :key="'T-' + adj.id"
          :adjudicator="adj"
          :debate-id="debateOrPanel.id"
          role="T"
        />
      </div>
    </slot>
  </div>
</template>
