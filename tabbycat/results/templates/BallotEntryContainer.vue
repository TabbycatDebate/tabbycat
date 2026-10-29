<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import BallotEntryHeader from './BallotEntryHeader.vue'
import BallotEntryScoresheet from './BallotEntryScoresheet.vue'
import BallotEntryFooter from './BallotEntryFooter.vue'


const props = defineProps({
  debateName: String,
  debateVenue: String,
  debateRound: String,
  isNew: Boolean,
  isAdmin: Boolean,
  isConfirmed: Boolean,
  isDiscarded: Boolean,
  currentStatus: String,
  hasIron: Boolean,
  blindEntry: Boolean,
  author: String,
  ballotAuthor: String,
  totalBallotsubs: Number,
  sendReceipts: Boolean,
})

const blindReveal = ref(false)
const blindFormIsValid = ref(true)
const ballotSheets = ref([])
const speakerScores = reactive({})
const teamScores = reactive({})
const showDuplicates = ref(false)

const canSubmit = computed(() => {
  const individualTeamScores = Object.values(teamScores)
  if (props.author === props.ballotAuthor && !props.isNew && !props.isAdmin) {
    return 'Ballot cannot be confirmed because you authored it'
  }
  if (individualTeamScores.indexOf(0) >= 0 || individualTeamScores.indexOf('') >= 0) {
    return 'Ballot cannot be submitted because a team score is missing'
  }
  if ([...new Set(individualTeamScores)].length < individualTeamScores.length) {
    return 'Ballot cannot be submitted because there is a tie'
  }
  if (!blindFormIsValid.value && blindReveal.value) {
    return 'Ballot cannot be confirmed because the re-entered data does not match the original'
  }
  return ''
})

const revealDuplicates = () => {
  showDuplicates.value = true
}

const revealBlindCheck = () => {
  blindReveal.value = true
}

const blindValidationFail = () => {
  blindFormIsValid.value = false
}

const setSpeakerScore = (teamPosition, speakerPosition, speakerScore) => {
  const existing = speakerScores[teamPosition] || {}
  existing[speakerPosition] = Number(speakerScore)
  speakerScores[teamPosition] = existing
  const teamScore = Object.values(existing).reduce((a, b) => a + b, 0)
  teamScores[teamPosition] = teamScore
}
onMounted(() => {
  const $ = window.$ || window.jQuery
  if (!$) {
    return
  }
  const ballotForm = $('#ballot').first()
  for (const sheet of $(ballotForm).find('div[data-type="sheet"]')) {
    const sheetData = {
      teams: [],
      title: sheet.getAttribute('data-title'),
      subtitle: sheet.getAttribute('data-subtitle'),
    }
    for (const team of $(sheet).find('div[data-type="team"]')) {
      const speakersData = []
      for (const speaker of $(team).find('div[data-type="speaker"]')) {
        speakersData.push({
          position: speaker.getAttribute('data-position'),
          nameField: $(speaker).find('select')[0],
          duplicateField: $(speaker).find('input[type="checkbox"]')[0],
          scoreField: $(speaker).find('input[type="number"]')[0],
        })
      }
      const side = team.getAttribute('data-side')
      sheetData.teams.push({
        name: team.getAttribute('data-name'),
        position: side,
        id: team.getAttribute('data-id'),
        speakers: speakersData,
      })
      speakerScores[side] = {}
    }
    ballotSheets.value.push(sheetData)
  }
})
</script>

<template>
  <div>
    <ballot-entry-header
      :debate="debateName"
      :venue="debateVenue"
      :round="debateRound"
      :is-new="isNew"
      :is-admin="isAdmin"
      :has-iron="hasIron"
      :show-duplicates="showDuplicates"
      @set-duplicates="revealDuplicates"
    />

    <div
      v-for="sheet in ballotSheets"
      class="card mt-3"
    >
      <div class="list-group list-group-flush">
        <div class="list-group-item pt-4">
          <h4
            class="card-title float-left mt-0 mb-2"
            v-html="sheet.title"
          />
          <div
            v-if="sheet.subtitle !== ''"
            class="badge badge-secondary float-right ml-2 mt-1"
          >
            <p class="mb-0">
              {{ sheet.subtitle }}
            </p>
          </div>
        </div>

        <div class="list-group-item scoresheet px-md-3 py-md-2 p-0">
          <div class="card-deck px-md-2 p-0">
            <ballot-entry-scoresheet
              v-for="team in sheet.teams.slice(0,2)"
              :key="team.id"
              :team-scores="teamScores"
              :team="team"
              :teams-count="sheet.teams.length"
              :has-iron="hasIron"
              :is-new="isNew"
              :is-admin="isAdmin"
              :blind-entry="blindEntry"
              :blind-reveal="blindReveal"
              :show-duplicates="showDuplicates"
              @update-speaker-score="setSpeakerScore"
              @blind-validation-fail="blindValidationFail"
            />
          </div>
          <div
            v-if="sheet.teams.length > 2"
            class="card-deck px-md-2 p-0"
          >
            <ballot-entry-scoresheet
              v-for="team in sheet.teams.slice(2)"
              :key="team.id"
              :team-scores="teamScores"
              :team="team"
              :teams-count="sheet.teams.length"
              :has-iron="hasIron"
              :is-new="isNew"
              :is-admin="isAdmin"
              :blind-entry="blindEntry"
              :blind-reveal="blindReveal"
              :show-duplicates="showDuplicates"
              @update-speaker-score="setSpeakerScore"
              @blind-validation-fail="blindValidationFail"
            />
          </div>
        </div>
      </div>
    </div>

    <ballot-entry-footer
      :is-new="isNew"
      :is-admin="isAdmin"
      :can-submit="canSubmit"
      :send-receipts="sendReceipts"
      :is-confirmed="isConfirmed"
      :is-discarded="isDiscarded"
      :current-status="currentStatus"
      :author="author"
      :ballot-author="ballotAuthor"
      :total-ballotsubs="totalBallotsubs"
      :blind-entry="blindEntry"
      :blind-reveal="blindReveal"
      :blind-form-is-valid="blindFormIsValid"
      @reveal-blind-check="revealBlindCheck"
    />
  </div>
</template>
