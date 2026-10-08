<script setup>
import { onMounted, reactive, ref } from 'vue'

const props = defineProps({
  debate: String,
  venue: String,
  round: String,
  isNew: Boolean,
  showDuplicates: Boolean,
  hasIron: Boolean,
  isAdmin: Boolean,
})

const emit = defineEmits(['set-duplicates'])

const selectedMotion = ref('')
const motionSelectionEnabled = ref(false)
const motionVetoesEnabled = ref(false)
const motionVetoes = reactive({})
const motionOptions = reactive({})
const ironStatus = ref(props.hasIron ? 'Yes' : 'No')

const setSelected = () => {
  const $ = window.$ || window.jQuery
  if (!$) {
    return
  }
  const motionData = $('#ballot').first().find('div[data-type="motion_selection"]')
  if (motionData.length > 0) {
    for (const option of $(motionData[0]).find('option')) {
      if (option.getAttribute('value') === selectedMotion.value) {
        option.setAttribute('selected', '')
      } else {
        option.removeAttribute('selected')
      }
    }
  }
}

const setVetoed = (team) => {
  const $ = window.$ || window.jQuery
  if (!$) {
    return
  }
  const veto = motionVetoes[team]
  if (!veto?.element) {
    return
  }
  for (const option of $(veto.element).find('option')) {
    if (option.getAttribute('value') === veto.value) {
      option.setAttribute('selected', '')
    } else {
      option.removeAttribute('selected')
    }
  }
}

const setIron = () => {
  if (ironStatus.value === 'Yes') {
    emit('set-duplicates', {})
  }
}

onMounted(() => {
  const $ = window.$ || window.jQuery
  if (!$) {
    return
  }

  const ballotForm = $('#ballot').first()

  const motionData = $(ballotForm).find('div[data-type="motion_selection"]')
  if (motionData.length > 0) {
    if ($(motionData[0]).find('option').length > 0) {
      motionSelectionEnabled.value = true
      for (const option of $(motionData[0]).find('option')) {
        if (option.getAttribute('value') != null && option.getAttribute('value')) {
          const optionID = option.getAttribute('value')
          motionOptions[optionID] = option.innerText
          if (option.getAttribute('selected') != null) {
            selectedMotion.value = optionID
          }
        }
      }
    }
  }

  const motionVetoesEls = $(ballotForm).find('div[data-type="motion_veto"]')
  if (motionVetoesEls.length > 0) {
    motionVetoesEnabled.value = true
    if (Object.keys(motionOptions).length === 0) {
      for (const option of $(motionVetoesEls[0]).find('option')) {
        if (option.getAttribute('value') != null && option.getAttribute('value')) {
          const optionID = option.getAttribute('value')
          motionOptions[optionID] = option.innerText
        }
      }
    }
    for (const teamVeto of $(motionVetoesEls)) {
      const teamName = $(teamVeto).find('label')[0].innerText
      for (const option of $(teamVeto).find('option')) {
        if (option.getAttribute('selected') != null) {
          motionVetoes[teamName] = { value: option.getAttribute('value'), element: teamVeto }
        }
      }
    }
  }
})
</script>

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

      <div
        v-if="motionSelectionEnabled"
        class="list-group-item pb-3 pt-3"
      >
        <div class="form-group">
          <label>Selected Motion</label>
          <select
            v-model="selectedMotion"
            class="required custom-select form-control"
            :disabled="!isNew && !isAdmin"
            tabindex="1"
            @change="setSelected()"
          >
            <option
              value=""
              :selected="selectedMotion === ''"
            >
              ---------
            </option>
            <option
              v-for="(motionText, motionID) in motionOptions"
              :value="motionID"
            >
              {{ motionText }}
            </option>
          </select>
        </div>
      </div>

      <div
        v-if="isAdmin && motionVetoesEnabled && !motionSelectionEnabled"
        class="list-group-item pb-3 pt-3 list-group-item-warning"
      >
        <div class="form-group">
          The "motion vetoes" preference is enabled, but the "motion selection" preference is not.
          If running an Australs-stype tournament you probably want both enabled. Motion
          selection can be enabled in the "Data Entry" section of your tournament's configuration.
        </div>
      </div>

      <div
        v-if="motionVetoesEnabled"
        class="list-group-item pb-3 pt-3"
      >
        <div class="row">
          <div
            v-for="(teamVeto, team, index) in motionVetoes"
            class="form-group col-lg-6"
          >
            <label>{{ team }}'s Veto</label>
            <select
              v-model="motionVetoes[team]['value']"
              class="required custom-select form-control"
              :disabled="!isNew && !isAdmin"
              :tabindex="index + 1"
              @change="setVetoed(team)"
            >
              <option
                value=""
                :selected="motionVetoes[team]['value'] === ''"
              >
                ---------
              </option>
              <option
                v-for="(motionText, motionID) in motionOptions"
                :value="motionID"
              >
                {{ motionText }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="list-group-item pb-3 pt-3">
        <div
          v-if="!showDuplicates"
          class="form-group"
        >
          <select
            v-model="ironStatus"
            class="required custom-select form-control"
            :disabled="!isNew && !isAdmin"
            :tabindex="4"
            @change="setIron()"
          >
            <option value="No">
              No speakers spoke twice (no 'iron-person' speeches)
            </option>
            <option value="Yes">
              A speaker spoke twice (an 'iron-person' speech)
            </option>
          </select>
        </div>
        <div
          v-if="showDuplicates"
          class="alert alert-info mb-0"
        >
          Speeches marked as 'duplicates' are hidden from the speaker tab and often need to be
          tracked in order to determine break eligibility. If a speaker is 'iron-personing' you would
          typically set their lowest-scoring speech as the 'duplicate'.
        </div>
      </div>
    </div>
  </div>
</template>
