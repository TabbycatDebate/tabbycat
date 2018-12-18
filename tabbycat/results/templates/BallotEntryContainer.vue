<template>
  <div>

    <ballot-entry-header :debate="debateName" :venue="debateVenue" :round="debateRound"
                         :is-new="isNew" :show-duplicates="showDuplicates"
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
              v-on:update-team-score="calculateTeamRanks" :team-scores="teamScores"
              :team="team" :key="team.id" :teams-count="sheet.teams.length"
              :show-duplicates="showDuplicates">
            </ballot-entry-scoresheet>
          </div>
          <div v-if="sheet.teams.length > 2" class="card-deck px-md-2 p-0" >
            <ballot-entry-scoresheet
              v-for="team in sheet.teams.slice(2)"
              v-on:update-team-score="calculateTeamRanks" :team-scores="teamScores"
              :team="team" :key="team.id" :teams-count="sheet.teams.length"
              :show-duplicates="showDuplicates">
            </ballot-entry-scoresheet>
          </div>
        </div>

      </div>
    </div>

    <ballot-entry-footer
      :is-new="isNew" :send-receipts="sendReceipts"
      :author="author" :ballot-author="ballotAuthor"></ballot-entry-footer>

  </div>
</template>

<script>
import BallotEntryHeader from './BallotEntryHeader.vue'
import BallotEntryScoresheet from './BallotEntryScoresheet.vue'
import BallotEntryFooter from './BallotEntryFooter.vue'

export default {
  mixins: [ ],
  components: { BallotEntryHeader, BallotEntryScoresheet, BallotEntryFooter },
  props: {
    debateName: String,
    debateVenue: String,
    debateRound: String,
    isNew: Boolean,
    author: String,
    ballotAuthor: String,
    sendReceipts: Boolean,
  },
  data: function () {
    return {
      ballotSheets: [],
      teamScores: {},
      showDuplicates: false,
    }
  },
  methods: {
    revealDuplicates: function () {
      console.log('reveal iro')
      this.showDuplicates = true
    },
    calculateTeamRanks: function (position, score) {
      this.$set(this.teamScores, position, score)
    },
  },
  mounted: function () {
    let ballotForm = $('#ballot').first()
    for (let sheet of ballotForm.find('div[data-type="sheet"]')) {
      var sheetData = {
        'teams': [],
        'title': sheet.getAttribute('data-title'),
        'subtitle': sheet.getAttribute('data-subtitle'),
      }
      for (let team of $(sheet).children()) {
        var speakersData = []
        for (let speaker of $(team).children()) {
          speakersData.push({
            'position': speaker.getAttribute('data-position'),
            'nameField': $(speaker).find('select')[0],
            'duplicateField': $(speaker).find('input[type="checkbox"]')[0],
            'scoreField': $(speaker).find('input[type="number"]')[0],
          })
        }
        sheetData['teams'].push({
          'name': team.getAttribute('data-name'),
          'position': team.getAttribute('data-side'),
          'id': team.getAttribute('data-id'),
          'speakers': speakersData,
        })
      }
      this.ballotSheets.push(sheetData)
    }
  },
}
</script>
