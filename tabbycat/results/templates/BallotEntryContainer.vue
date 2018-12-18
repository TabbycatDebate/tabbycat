<template>
  <div>

    <ballot-entry-header :debate-name="debateName" :is-new="isNew"></ballot-entry-header>

    <div class="card mt-3" v-for="sheet in ballotSheets">
      <div class="list-group list-group-flush">

        <div class="list-group-item pt-4">
          <h4 class="card-title float-left mt-0 mb-2">Scoresheet</h4>
          <div class="badge badge-secondary float-right ml-2 mt-1">
            <p class="mb-0">Panellist Deets</p>
          </div>
        </div>

        <div class="list-group-item scoresheet px-md-3 py-md-2 p-0">
          <div class="card-deck px-md-2 p-0">
            <ballot-entry-scoresheet v-for="team in sheet.teams.slice(0,2)"
              :team="team" :key="team.id"></ballot-entry-scoresheet>
          </div>
          <div v-if="sheet.teams.length > 2" class="card-deck px-md-2 p-0" >
            <ballot-entry-scoresheet v-for="team in sheet.teams.slice(2)"
              :team="team" :key="team.id"></ballot-entry-scoresheet>
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
    isNew: Boolean,
    author: String,
    ballotAuthor: String,
    sendReceipts: Boolean,
  },
  data: function () {
    return {
      ballotSheets: [],
    }
  },
  methods: { },
  mounted: function () {
    let ballotForm = $('#ballot').first()
    for (let sheet of ballotForm.children()) {
      var sheetData = { 'teams': [] }
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
