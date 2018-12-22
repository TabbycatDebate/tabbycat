<template>

  <div class="list-group-item">

    <div v-if="blindEntry" class="row">

      <div class="col-2 d-flex align-items-center mb-0 pl-2 pr-0 h6 text-muted">
        {{ speaker.position }}
      </div>

      <div class="col mb-0 pr-md-1 pr-md-2 pr-1 pl-1 form-group">
        <select v-model="speakerNameShadow" :disabled="blindReveal"
          :class="['custom-select mb-2', blindSpeakerMatches ? '' : 'is-invalid bg-dark text-white']">
          <option v-bind:value="0" selected>{{ selectOptions[0].text }}</option>
          <option v-for="option in selectOptions.slice(1)" v-bind:value="option.value">
            {{ option.text }}
          </option>
        </select>
        <span class="text-danger" v-if="blindReveal && !blindSpeakerMatches">Does not match</span>
        <div class="small pt-0 m-0" v-if="showDuplicates || speakerDuplicate">
          <input tabindex="-1" type="checkbox" v-model.number="speakerDuplicateShadow"
                 :disabled="blindReveal" />
          <span class="mt-2"></span>
          <label class="ml-2">Mark as a duplicate speech</label>
        </div>
      </div>

      <div class="col-3 form-group pr-1 pl-1">
        <input :class="['form-control mb-2', blindScoreMatches ? '' : 'is-invalid bg-dark text-white']"
               :readonly="blindReveal" v-model.number="speakerScoreShadow" v-bind="scoreAttributes">
        <span class="text-danger" v-if="blindReveal && !blindScoreMatches">No match</span>
      </div>

    </div>

    <div v-if="blindReveal || !blindEntry || isNew" class="row mt-2">

      <div class="col-2 d-flex align-items-center mb-0 pl-2 pr-0 h6 text-muted">
        <span v-if="blindEntry">Draft</span>
        <span v-if="!blindEntry">{{ speaker.position }}</span>
      </div>

      <div class="col mb-0 pr-md-1 pr-md-2 pr-1 pl-1 form-group">

        <select :class="['custom-select', speakerError ? 'border-danger text-danger' : '',
                                          !blindSpeakerMatches ? 'is-invalid' : '']"
                v-model="speakerName" v-bind="selectAttributes" :disabled="!isNew"
                @change="setShadowSpeaker(speakerName)">
          <option v-for="option in selectOptions" v-bind:value="option.value"
                  :selected="speakerName === option.value">
            {{ option.text }}
          </option>
        </select>
        <label v-if="speakerError" class="error pt-2">{{ speakerError }}</label>
        <div class="small pt-0 m-0" v-if="showDuplicates || speakerDuplicate">
          <input tabindex="-1" type="checkbox" v-model.number="speakerDuplicate"
                 @change="setShadowDuplicate(speakerScore)" :disabled="!isNew" />
          <span class="mt-2"></span>
          <label class="ml-2">Mark as a duplicate speech</label>
        </div>

      </div>

      <div class="col-3 form-group pr-1 pl-1">
        <input :class="['form-control', scoreError ? 'border-danger text-danger' : '',
                                        blindScoreMatches ? '' : 'is-invalid']"
               @change="setShadowScore(speakerScore)" :readonly="!isNew"
               v-model.number="speakerScore" v-bind="scoreAttributes">
        <label v-if="scoreError" class="error pt-2">{{ scoreError }}</label>
      </div>

    </div>

  </div>

</template>

<script>

export default {
  props: {
    speaker: Object,
    team: Object,
    index: Number,
    showDuplicates: Boolean,
    isNew: Boolean,
    blindEntry: Boolean,
    blindReveal: Boolean,
  },
  data: function () {
    return {
      speakerName: null,
      speakerDuplicate: false,
      speakerScore: null,
      speakerNameShadow: 0,
      speakerDuplicateShadow: false,
      speakerScoreShadow: null,
    }
  },
  mounted: function () {
    this.speakerName = this.speaker.nameField.options[this.speaker.nameField.selectedIndex].value
    this.speakerDuplicate = this.speaker.duplicateField.checked
    this.speakerScore = Number(this.speaker.scoreField.getAttribute('value'))
    this.speaker.duplicateField.setAttribute('tabindex', -1) // Remove old tab order
    this.$nextTick(function () {
      this.$emit('set-speaker-score', this.team.position, this.speaker.position, this.speakerScore)
    })
  },
  methods: {
    setShadowScore: function (setValue) {
      document.getElementById(this.speaker.scoreField.getAttribute('id')).value = setValue
      this.$emit('set-speaker-score', this.team.position, this.speaker.position, this.speakerScore)
    },
    setShadowSpeaker: function (setValue) {
      let select = document.getElementById(this.speaker.nameField.getAttribute('id'))
      for (let option of select.options) {
        if (option.value === setValue) {
          option.selected = true
        }
      }
    },
    setShadowDuplicate: function (setValue) {
      document.getElementById(this.speaker.duplicateField.getAttribute('id')).checked = setValue
    },
  },
  computed: {
    blindSpeakerMatches: function () {
      if (!this.blindReveal || this.speakerNameShadow === this.speakerName) {
        return true
      }
      this.$emit('blind-validation-fail')
      return false
    },
    blindScoreMatches: function () {
      if (!this.blindReveal || this.speakerScoreShadow === this.speakerScore) {
        return true
      }
      this.$emit('blind-validation-fail')
      return false
    },
    speakerError: function () {
      // return 'Speaker selected multiple times but none is marked as a duplicate'
      return false
    },
    scoreError: function () {
      if (this.speakerScore !== null && this.speakerScore > 9) {
        // > 9 is so it doesn't flash up before the full score has been typed
        if (this.speakerScore > this.scoreAttributes.max) {
          return 'Score larger than allowed'
        }
        if (this.speakerScore < this.scoreAttributes.min) {
          return 'Score smaller than allowed'
        }
      }
      return false
    },
    selectOptions: function () {
      var options = []
      for (let speaker of this.speaker.nameField) {
        options.push({ 'text': speaker.textContent, 'value': speaker.getAttribute('value') })
      }
      return options
    },
    selectAttributes: function () {
      var attributes = {
        'tabindex': this.speaker.nameField.getAttribute('tabindex'),
        'data-counterpart': this.speaker.nameField.getAttribute('id'),
      }
      this.speaker.nameField.setAttribute('tabindex', -1) // Remove old tab order
      return attributes
    },
    scoreAttributes: function () {
      var attributes = {}
      for (let label of ['step', 'min', 'max', 'tabindex', 'type']) {
        attributes[label] = this.speaker.scoreField.getAttribute(label)
      }
      attributes['data-counterpart'] = this.speaker.scoreField.getAttribute('id')
      this.speaker.scoreField.setAttribute('tabindex', -1) // Remove old tab order
      return attributes
    },
  },
}
</script>
