<script setup>
import { computed } from 'vue'
import BallotEntrySpeaker from './BallotEntrySpeaker.vue'

const props = defineProps({
  team: Object,
  teamScores: Object,
  teamsCount: Number,
  showDuplicates: Boolean,
  isNew: Boolean,
  isAdmin: Boolean,
  blindEntry: Boolean,
  blindReveal: Boolean,
  hasIron: Boolean,
})

const emit = defineEmits(['update-speaker-score', 'blind-validation-fail'])

const rankLabels = {
  1: '1st',
  2: '2nd',
  3: '3rd',
  4: '4th',
  '?': '?',
  tie: 'TIE',
}

const rankClasses = {
  1: 'btn-success',
  2: 'btn-info',
  3: 'btn-warning',
  4: 'btn-danger',
  '?': 'btn-secondary',
  tie: 'btn-dark',
}

const teamPoints = computed(() => props.teamScores?.[props.team.position])

const teamMargin = computed(() => {
  const nonZeroScores = Object.values(props.teamScores || {}).filter(s => s > 0)
  if (nonZeroScores.length !== props.teamsCount) { return '?   ' }
  const top = Object.values(props.teamScores).sort().slice(-1)
  return props.teamScores[props.team.position] - top
})

const teamRank = computed(() => {
  const nonZeroScores = Object.values(props.teamScores || {}).filter(s => s > 0)
  if (nonZeroScores.length !== props.teamsCount) { return '?' }
  const scores = Object.values(props.teamScores).sort((a, b) => a - b).reverse()
  for (const [index, score] of scores.entries()) {
    if (score === props.teamScores[props.team.position]) {
      if (Object.values(props.teamScores).filter(s => s === score).length > 1) {
        return 'tie'
      }
      return index + 1
    }
  }
  return '?'
})

const setSpeakerScore = (teamPosition, speakerPosition, speakerScore) => {
  emit('update-speaker-score', teamPosition, speakerPosition, speakerScore)
}

const blindValidationFail = () => {
  emit('blind-validation-fail', {})
}
</script>

<template>
  <div class="card pr-0 mr-0 m-2">
    <div class="list-group list-group-flush">
      <div class="list-group-item pb-0">
        <div class="row">
          <!-- team-name class used by unknown sides switcher -->
          <div
            class="col mr-auto card-title pl-md-2 pl-1"
            v-html="team.name"
          />
          <div class="col-auto card-subtitle text-muted text-right pt-2 pr-md-2 pr-1">
            <h6>{{ team.position }}</h6>
          </div>
        </div>
      </div>

      <ballot-entry-speaker
        v-for="(speaker, index) in team.speakers"
        :key="index"
        :is-new="isNew"
        :is-admin="isAdmin"
        :blind-entry="blindEntry"
        :blind-reveal="blindReveal"
        :speaker="speaker"
        :team="team"
        :index="index"
        :show-duplicates="showDuplicates"
        :has-iron="hasIron"
        @set-speaker-score="setSpeakerScore"
        @blind-validation-fail="blindValidationFail"
      />

      <div class="list-group-item">
        <div class="row">
          <div class="col offset-md-2 mb-0 pr-md-2 pr-1 pl-1">
            <div class="btn-group d-flex">
              <button
                tabindex="-1"
                class="btn btn-outline-secondary btn-no-hover"
                readonly
              >
                R<span class="d-none d-md-inline">ank</span>
              </button>
              <button
                tabindex="-1"
                :class="['btn btn-no-hover flex-grow-1 text-monospace border-right-0 ', rankClasses[teamRank]]"
                readonly
              >
                {{ rankLabels[teamRank] }}
              </button>
              <button
                tabindex="-1"
                class="btn btn-outline-secondary btn-no-hover"
                readonly
              >
                M<span class="d-none d-md-inline">argin</span>
              </button>
              <button
                tabindex="-1"
                :class="['btn btn-no-hover flex-grow-1 text-monospace', rankClasses[teamRank]]"
                readonly
              >
                <span v-if="teamMargin >= 0">+</span>{{ teamMargin }}
              </button>
            </div>
          </div>

          <div class="col-3 form-group pr-1 pl-1">
            <button
              tabindex="-1"
              :class="['btn btn-block btn-no-hover', rankClasses[teamRank]]"
              readonly
            >
              {{ teamPoints }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
