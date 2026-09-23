<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

const props = defineProps({
  speaker: Object,
  team: Object,
  index: Number,
  showDuplicates: Boolean,
  isNew: Boolean,
  isAdmin: Boolean,
  blindEntry: Boolean,
  blindReveal: Boolean,
  hasIron: Boolean,
})

const emit = defineEmits(['set-speaker-score', 'blind-validation-fail'])

const speakerName = ref(null)
const speakerDuplicate = ref(false)
const speakerScore = ref(null)

const speakerNameShadow = ref(0)
const speakerDuplicateShadow = ref(false)
const speakerScoreShadow = ref(null)

const selectOptions = computed(() => {
  const options = []
  for (const speakerOpt of props.speaker.nameField) {
    options.push({ text: speakerOpt.textContent, value: speakerOpt.getAttribute('value') })
  }
  return options.sort((a, b) => a.text.localeCompare(b.text))
})

const selectAttributes = computed(() => {
  const attributes = {
    tabindex: props.speaker.nameField.getAttribute('tabindex'),
    'data-counterpart': props.speaker.nameField.getAttribute('id'),
  }
  props.speaker.nameField.setAttribute('tabindex', -1)
  return attributes
})

const scoreAttributes = computed(() => {
  const attributes = {}
  for (const label of ['step', 'min', 'max', 'tabindex', 'type']) {
    attributes[label] = props.speaker.scoreField.getAttribute(label)
  }
  attributes['data-counterpart'] = props.speaker.scoreField.getAttribute('id')
  props.speaker.scoreField.setAttribute('tabindex', -1)
  return attributes
})

const speakerScoreForBallotType = computed(() => {
  if (props.blindEntry && !props.isNew) {
    return speakerScoreShadow.value
  }
  return speakerScore.value
})

const setShadowScore = (setValue) => {
  document.getElementById(props.speaker.scoreField.getAttribute('id')).value = setValue
  emit('set-speaker-score', props.team.position, props.speaker.position, speakerScoreForBallotType.value)
}

const setShadowSpeaker = (setValue) => {
  const select = document.getElementById(props.speaker.nameField.getAttribute('id'))
  for (const option of select.options) {
    if (option.value === setValue) {
      option.selected = true
    }
  }
}

const setShadowDuplicate = (setValue) => {
  document.getElementById(props.speaker.duplicateField.getAttribute('id')).checked = setValue
}

const blindSpeakerMatches = computed(() => {
  if (!props.blindReveal || speakerNameShadow.value === speakerName.value) {
    return true
  }
  emit('blind-validation-fail', {})
  return false
})

const blindDuplicateMatches = computed(() => {
  if (!props.blindReveal || speakerDuplicate.value === speakerDuplicateShadow.value) {
    return true
  }
  emit('blind-validation-fail', {})
  return false
})

const blindScoreMatches = computed(() => {
  if (!props.blindReveal || speakerScoreShadow.value === speakerScore.value) {
    return true
  }
  emit('blind-validation-fail', {})
  return false
})

const speakerError = computed(() => false)

const scoreError = computed(() => {
  if (speakerScore.value !== null && speakerScore.value > 9) {
    if (speakerScore.value > scoreAttributes.value.max) {
      return 'Score larger than allowed'
    }
    if (speakerScore.value < scoreAttributes.value.min) {
      return 'Score smaller than allowed'
    }
  }
  return false
})

onMounted(async () => {
  speakerName.value = props.speaker.nameField.options[props.speaker.nameField.selectedIndex].value
  speakerDuplicate.value = props.speaker.duplicateField.checked
  speakerScore.value = Number(props.speaker.scoreField.getAttribute('value'))
  props.speaker.duplicateField.setAttribute('tabindex', -1)
  await nextTick()
  emit('set-speaker-score', props.team.position, props.speaker.position, speakerScoreForBallotType.value)
})
</script>

<template>
  <div class="list-group-item">
    <div
      v-if="blindEntry"
      class="row"
    >
      <div
        class="col-2 d-flex align-items-center mb-0 pl-2 pr-0 h6 text-muted"
        v-html="blindReveal ? 'Re-Entry of ' + speaker.position : speaker.position"
      />

      <div class="col mb-0 pr-md-1 pr-md-2 pr-1 pl-1 form-group">
        <select
          v-model="speakerNameShadow"
          :disabled="blindReveal"
          v-bind="selectAttributes"
          :class="['custom-select mb-2', !blindSpeakerMatches && blindReveal ? 'is-invalid bg-dark text-white' : '',
                   blindSpeakerMatches && blindReveal ? 'is-valid' : '']"
        >
          <option
            :value="0"
            selected
          >
            {{ selectOptions[0].text }}
          </option>
          <option
            v-for="option in selectOptions.slice(1)"
            :value="option.value"
          >
            {{ option.text }}
          </option>
        </select>
        <span
          v-if="blindReveal && !blindSpeakerMatches"
          class="text-danger"
        >
          Speaker does not match
        </span>
        <span
          v-if="blindReveal && !blindDuplicateMatches"
          class="text-danger"
        >
          Duplicate status does not match
        </span>
        <div
          v-if="showDuplicates || speakerDuplicate || hasIron"
          class="small pt-0 m-0"
        >
          <input
            :id="'dupeCheck' + speaker.position"
            v-model.number="speakerDuplicateShadow"
            tabindex="-1"
            type="checkbox"
            :disabled="blindReveal"
          >
          <span class="mt-2" />
          <label
            :for="'dupeCheck' + speaker.position"
            :class="['ml-2 hoverable', blindDuplicateMatches ? '' : 'text-danger']"
          >
            Mark as a duplicate speech
          </label>
        </div>
      </div>

      <div class="col-3 form-group pr-1 pl-1">
        <input
          v-model.number="speakerScoreShadow"
          :class="['form-control mb-2', !blindScoreMatches && blindReveal ? 'is-invalid bg-dark text-white' : '',
                   blindScoreMatches && blindReveal ? 'is-valid' : '']"
          :readonly="blindReveal"
          v-bind="scoreAttributes"
          @change="setShadowScore(speakerScoreShadow)"
        >
        <span
          v-if="blindReveal && !blindScoreMatches"
          class="text-danger"
        >No match</span>
      </div>
    </div>

    <div
      v-if="blindReveal || !blindEntry || isNew"
      class="row"
    >
      <div
        :class="['col-2 d-flex align-items-center mb-0 pl-2 pr-0 h6',
                 blindEntry ? 'text-primary' : 'text-muted']"
      >
        <span v-if="blindEntry">Draft</span>
        <span v-if="!blindEntry">{{ speaker.position }}</span>
      </div>

      <div class="col mb-0 pr-md-1 pr-md-2 pr-1 pl-1 form-group">
        <select
          v-model="speakerName"
          :class="['custom-select', speakerError ? 'border-danger text-danger' : '',
                   !blindSpeakerMatches && blindEntry ? 'is-invalid' : '',
                   blindSpeakerMatches && blindEntry ? 'is-valid' : '']"
          v-bind="selectAttributes"
          :disabled="!isNew && !isAdmin"
          @change="setShadowSpeaker(speakerName)"
        >
          <option
            v-for="option in selectOptions"
            :value="option.value"
            :selected="speakerName === option.value"
          >
            {{ option.text }}
          </option>
        </select>
        <label
          v-if="speakerError"
          class="error pt-2"
        >{{ speakerError }}</label>
        <div
          v-if="showDuplicates || speakerDuplicate || hasIron"
          class="small pt-0 m-0"
        >
          <input
            :id="'check' + speaker.position"
            v-model.number="speakerDuplicate"
            tabindex="-1"
            type="checkbox"
            :disabled="!isNew && !isAdmin"
            @change="setShadowDuplicate(speakerScore)"
          >
          <span class="mt-2" />
          <label
            :for="'check' + speaker.position"
            :class="['ml-2 hoverable', blindDuplicateMatches ? '' : 'text-danger']"
          >
            Mark as a duplicate speech
          </label>
        </div>
      </div>

      <div class="col-3 form-group pr-1 pl-1">
        <input
          v-model.number="speakerScore"
          :class="['form-control', scoreError ? 'border-danger text-danger' : '',
                   blindScoreMatches && blindEntry ? 'is-valid' : '',
                   !blindScoreMatches && blindEntry ? 'is-invalid' : '']"
          :readonly="!isNew && !isAdmin"
          v-bind="scoreAttributes"
          @change="setShadowScore(speakerScore)"
        >
        <label
          v-if="scoreError"
          class="error pt-2"
        >{{ scoreError }}</label>
      </div>
    </div>
  </div>
</template>
