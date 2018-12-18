<template>

  <div class="list-group-item">
    <div class="row">

      <div class="col-2 pt-2 p-lg-2 pr-0 p-1 speaker-position-label">
        {{ speaker.position }}
      </div>

      <div class="col mb-0 pr-md-2 pr-1 form-group">
        <select v-model="speakerName" class="custom-select" v-bind="selectAttributes">
          <option v-for="option in selectOptions" v-bind:value="option.value"
                  :selected="speakerName.value === option.value">
            {{ option.text }}
          </option>
        </select>

        <div class="small pt-0 m-0">
          <input type="checkbox" v-model.number="speakerDuplicate" @change="setShadowDuplicate(speakerScore)" />
          <span class="mt-2"></span>
          <label class="ml-2">Mark as a duplicate speech</label>
        </div>

      </div>

      <div class="col-4 form-group pr-md-2 pr-1 score">
        <input class="form-control" @change="setShadowScore(speakerScore)"
               v-model.number="speakerScore" v-bind="scoreAttributes">
      </div>

    </div>

  </div>

</template>

<script>

export default {
  props: { speaker: Object },
  data: function () {
    return {
      speakerName: this.speaker.nameField.options[this.speaker.nameField.selectedIndex].value,
      speakerDuplicate: this.speaker.duplicateField.checked,
      speakerScore: this.speaker.scoreField.getAttribute('value'),
    }
  },
  methods: {
    setShadowScore: function (setValue) {
      document.getElementById(this.speaker.scoreField.getAttribute('id')).value = setValue
    },
    setShadowDuplicate: function (setValue) {
      document.getElementById(this.speaker.duplicateField.getAttribute('id')).checked = setValue
    },
  },
  computed: {
    selectOptions: function () {
      var options = []
      for (let speaker of this.speaker.nameField) {
        options.push({ 'text': speaker.textContent, 'value': speaker.getAttribute('value') })
      }
      return options
    },
    selectAttributes: function () {
      return {
        'tabindex': this.speaker.nameField.getAttribute('tabindex'),
        'data-counterpart': this.speaker.nameField.getAttribute('id'),
      }
    },
    scoreAttributes: function () {
      var attributes = {}
      for (let label of ['step', 'min', 'max', 'tabindex', 'type']) {
        attributes[label] = this.speaker.scoreField.getAttribute(label)
      }
      attributes['data-counterpart'] = this.speaker.scoreField.getAttribute('id')
      return attributes
    },
  },
}
</script>
