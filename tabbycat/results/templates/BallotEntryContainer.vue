<template>
  <div>

    <ballot-entry-header :debate="debateName" :venue="debateVenue" :round="debateRound"
                         :is-new="isNew" :is-admin="isAdmin"
                         :has-iron="hasIron" :show-duplicates="showDuplicates"
                         v-on:set-duplicates="revealDuplicates">
    </ballot-entry-header>

    <div class="card mt-3" v-for="sheet in ballotSheets">
      <div class="list-group list-group-flush">

        <div class="list-group-item pt-4">
          <h4 class="card-title float-left mt-0 mb-2" v-html="sheet.title"></h4>
          <div class="badge badge-secondary float-right ml-2 mt-1" v-if="sheet.subtitle !== ''">
            <p class="mb-0">{{ sheet.subtitle }}</p>
          </div>
        </div>

        <div class="list-group-item scoresheet px-md-3 py-md-2 p-0">
          <div class="card-deck px-md-2 p-0">
            <ballot-entry-scoresheet
              v-for="team in sheet.teams.slice(0,2)"
              v-on:update-speaker-score="setSpeakerScore"
              v-on:blind-validation-fail="blindValidationFail" :team-scores="teamScores"
              :team="team" :key="team.id" :teams-count="sheet.teams.length" :has-iron="hasIron"
              :is-new="isNew" :is-admin="isAdmin" :blind-entry="blindEntry" :blind-reveal="blindReveal"
              :show-duplicates="showDuplicates">
            </ballot-entry-scoresheet>
          </div>
          <div v-if="sheet.teams.length > 2" class="card-deck px-md-2 p-0" >
            <ballot-entry-scoresheet
              v-for="team in sheet.teams.slice(2)"
              v-on:update-speaker-score="setSpeakerScore"
              v-on:blind-validation-fail="blindValidationFail" :team-scores="teamScores"
              :team="team" :key="team.id" :teams-count="sheet.teams.length" :has-iron="hasIron"
              :is-new="isNew" :is-admin="isAdmin" :blind-entry="blindEntry" :blind-reveal="blindReveal"
              :show-duplicates="showDuplicates">
            </ballot-entry-scoresheet>
          </div>
        </div>

      </div>
    </div>

    <ballot-entry-footer
      :is-new="isNew" :is-admin="isAdmin" :can-submit="canSubmit" :send-receipts="sendReceipts"
      :is-confirmed="isConfirmed" :is-discarded="isDiscarded" :current-status="currentStatus"
      :author="author" :ballot-author="ballotAuthor" :total-ballotsubs="totalBallotsubs"
      :blind-entry="blindEntry" :blind-reveal="blindReveal" :blind-form-is-valid="blindFormIsValid"
      v-on:reveal-blind-check="revealBlindCheck">
    </ballot-entry-footer>

  </div>
</template>

<script>
import BallotEntryHeader from './BallotEntryHeader.vue'
import BallotEntryScoresheet from './BallotEntryScoresheet.vue'
import BallotEntryFooter from './BallotEntryFooter.vue'

export default {
  mixins: [],
  components: { BallotEntryHeader, BallotEntryScoresheet, BallotEntryFooter },
  props: {
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
  },
  data: function () {
    return {
      blindReveal: false,
      blindFormIsValid: true,
      ballotSheets: [],
      speakerScores: {},
      teamScores: {},
      showDuplicates: false,
    }
  },
  computed: {
    canSubmit: function () {
      const individualTeamScores = Object.values(this.teamScores)
      if (this.author === this.ballotAuthor && !this.isNew && !this.isAdmin) {
        return 'Ballot cannot be confirmed because you authored it'
      }
      if (individualTeamScores.indexOf(0) >= 0 || individualTeamScores.indexOf('') >= 0) {
        return 'Ballot cannot be submitted because a team score is missing'
      }
      if ([...new Set(individualTeamScores)].length < individualTeamScores.length) {
        return 'Ballot cannot be submitted because there is a tie'
      }
      if (!this.blindFormIsValid && this.blindReveal) {
        return 'Ballot cannot be confirmed because the re-entered data does not match the original'
      }
      return ''
    },
  },
  methods: {
    revealDuplicates: function () {
      this.showDuplicates = true
    },
    revealBlindCheck: function () {
      this.blindReveal = true
    },
    blindValidationFail: function () {
      this.blindFormIsValid = false
    },
    setSpeakerScore: function (teamPosition, speakerPosition, speakerScore) {
      var changedScores = this.speakerScores[teamPosition]
      changedScores[speakerPosition] = Number(speakerScore)
      this.$set(this.speakerScores, teamPosition, changedScores)
      const teamScore = Object.values(changedScores).reduce((a, b) => a + b, 0)
      this.$set(this.teamScores, teamPosition, teamScore)
    },
  },
  mounted: function () {
    const ballotForm = $('#ballot').first()
    // Get per-adj scoresheets
    for (const sheet of $(ballotForm).find('div[data-type="sheet"]')) {
      var sheetData = {
        teams: [],
        title: sheet.getAttribute('data-title'),
        subtitle: sheet.getAttribute('data-subtitle'),
      }
      for (const team of $(sheet).find('div[data-type="team"]')) {
        var speakersData = []
        for (const speaker of $(team).find('div[data-type="speaker"]')) {
          speakersData.push({
            position: speaker.getAttribute('data-position'),
            nameField: $(speaker).find('select')[0],
            duplicateField: $(speaker).find('input[type="checkbox"]')[0],
            scoreField: $(speaker).find('input[type="number"]')[0],
          })
        }
        sheetData.teams.push({
          name: team.getAttribute('data-name'),
          position: team.getAttribute('data-side'),
          id: team.getAttribute('data-id'),
          speakers: speakersData,
        })
        this.speakerScores[team.getAttribute('data-side')] = {}
      }
      this.ballotSheets.push(sheetData)
    }
  },
}
</script>
