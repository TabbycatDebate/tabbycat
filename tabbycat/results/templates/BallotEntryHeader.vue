<template>
  <div class="card">
    <div class="list-group list-group-flush">

      <div class="list-group-item pt-4">
        <h4 class="card-title mt-0 mb-2 d-inline-block">
          <span v-if="isNew">New Ballot Set</span>
          <span v-if="!isNew">Edit Ballot Set</span>
        </h4>
        <div class="badge badge-secondary float-right ml-2 mt-1">
          {{ debate }}
        </div>
        <div class="badge badge-secondary float-right ml-2 mt-1">
          {{ round }}
        </div>
        <div class="badge badge-secondary float-right ml-2 mt-1">
          {{ venue }}
        </div>
      </div>
      <!-- TODO: Side choosing -->

      <!-- TODO: Motion choosing -->
      <div class="list-group-item pb-3 pt-3">
        <div class="form-group">
          <label>Selected Motion</label>
          <select class="required custom-select form-control" @change="setSelected()"
                  v-model="selectedMotion" :disabled="!isNew && !isAdmin" tabindex="1">
            <option value="" :selected="selectedMotion === ''">---------</option>
            <option v-for="(motionText, motionID) in motionOptions" :value="motionID">
              {{ motionText }}
            </option>
          </select>
        </div>
      </div>
      <!-- TODO: Veto choosing -->
      <div class="list-group-item pb-3 pt-3">
        <div class="row">
          <div class="form-group col-lg-6" v-for="(teamVeto, team, index) in motionVetoes">
            <label>{{ team }}'s Veto</label>
            <select class="required custom-select form-control" @change="setVetoed(team)"
                    v-model="motionVetoes[team]['value']" :disabled="!isNew && !isAdmin" :tabindex="index + 1">
              <option value="" :selected="motionVetoes[team]['value'] === ''">---------</option>
              <option v-for="(motionText, motionID) in motionOptions" :value="motionID">
                {{ motionText }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="list-group-item pb-3 pt-3">
        <div class="form-group" v-if="!showDuplicates">
          <select class="required custom-select form-control" v-model="ironStatus"
                  @change="setIron()" :disabled="!isNew && !isAdmin" :tabindex="4">
            <option value="No">
              No speakers spoke twice (no 'iron-person' speeches)
            </option>
            <option value="Yes">
              A speaker spoke twice (an 'iron-person' speech)
            </option>
          </select>
        </div>
        <div class="alert alert-info mb-0" v-if="showDuplicates">
          Speeches marked as 'duplicates' are hidden from the speaker tab and often need to be
          tracked in order to determine break eligibility. If a speaker is 'iron-manning' you would
          typically set their lowest-scoring speech as the 'duplicate'.
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  props: {
    debate: String,
    venue: String,
    round: String,
    isNew: Boolean,
    showDuplicates: Boolean,
    hasIron: Boolean,
    isAdmin: Boolean,
  },
  data: function () {
    return {
      selectedMotion: '',
      motionVetoes: {},
      motionOptions: {},
      ironStatus: this.hasIron ? 'Yes' : 'No',
    }
  },
  methods: {
    setSelected: function () {
      let motionData = $('#ballot').first().find('div[data-type="motion_selection"]')
      if (motionData.length > 0) {
        for (let option of $(motionData[0]).find('option')) {
          if (option.getAttribute('value') === this.selectedMotion) {
            option.setAttribute('selected', '')
          } else {
            option.removeAttribute('selected')
          }
        }
      }
    },
    setVetoed: function (team) {
      for (let option of $(this.motionVetoes[team]['element']).find('option')) {
        if (option.getAttribute('value') === this.motionVetoes[team]['value']) {
          option.setAttribute('selected', '')
        } else {
          option.removeAttribute('selected')
        }
      }
    },
    setIron: function () {
      if (this.ironStatus === 'Yes') {
        this.$emit('set-duplicates')
      }
    },
  },
  mounted: function () {
    let ballotForm = $('#ballot').first()
    // Get ballot selection info
    let motionData = $(ballotForm).find('div[data-type="motion_selection"]')
    if (motionData.length > 0) {
      for (let option of $(motionData[0]).find('option')) {
        if (option.getAttribute('value') != null && option.getAttribute('value')) {
          let optionID = option.getAttribute('value')
          this.$set(this.motionOptions, optionID, option.innerText) // Must be reactive
          if (option.getAttribute('selected') != null) {
            this.selectedMotion = optionID
          }
        }
      }
    }
    // Get ballot veto info
    let motionVetoes = $(ballotForm).find('div[data-type="motion_veto"]')
    for (let teamVeto of $(motionVetoes)) {
      let teamName = $(teamVeto).find('label')[0].innerText
      for (let option of $(teamVeto).find('option')) {
        if (option.getAttribute('selected') != null) {
          let optionDictionary = { 'value': option.getAttribute('value'), 'element': teamVeto }
          this.$set(this.motionVetoes, teamName, optionDictionary) // Must be reactive
        }
      }
    }
  },
}
</script>
