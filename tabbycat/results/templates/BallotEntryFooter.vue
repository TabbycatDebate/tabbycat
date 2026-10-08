<script setup>
import { ref } from 'vue'

const props = defineProps({
  isNew: Boolean,
  isAdmin: Boolean,
  currentStatus: String,
  canSubmit: String,
  sendReceipts: Boolean,
  isConfirmed: Boolean,
  isDiscarded: Boolean,
  blindEntry: Boolean,
  blindReveal: Boolean,
  totalBallotsubs: Number,
  blindFormIsValid: Boolean,
})

const emit = defineEmits(['reveal-blind-check'])

const status = ref(props.currentStatus)
const submitting = ref(false)
const confirmed = ref(props.isConfirmed)
const discarded = ref(props.isDiscarded)

const setStatus = (state) => {
  document.getElementById('id_debate_result_status').value = state
}

const setConfirmed = (state) => {
  document.getElementById('id_confirmed').value = state ? 'True' : 'False'
}

const setDiscarded = (state) => {
  document.getElementById('id_discarded').value = state ? 'True' : 'False'
}

const submit = () => {
  submitting.value = true
  document.getElementById('resultsForm').submit()
}

const check = () => {
  emit('reveal-blind-check', {})
}

const invalidate = () => {
  setStatus(props.totalBallotsubs > 1 ? 'D' : 'N')
  setConfirmed(false)
  setDiscarded(true)
  submit()
}
</script>

<template>
  <div class="card mt-3">
    <div class="list-group list-group-flush">
      <div
        v-if="isAdmin"
        class="list-group-item"
      >
        <h4 class="card-title mt-0 mb-2 d-inline-block">
          Ballot Status
        </h4>
        <h4 class="text-secondary float-right">
          <small>only the confirmed ballot set will affect this debate's result</small>
        </h4>
      </div>
      <div
        v-if="isAdmin"
        class="list-group-item"
      >
        <div class="row">
          <div class="col-lg-2 pt-1">
            <div class="form-check form-check-inline">
              <input
                id="shadowConfirmed"
                v-model="confirmed"
                type="checkbox"
                tabindex="117"
                class="form-check-input"
                @change="setConfirmed(confirmed)"
              >
              <label
                class="form-check-label pt-0"
                for="shadowConfirmed"
              >Confirmed</label>
            </div>
          </div>
          <div class="col-lg-2 pt-1">
            <div class="form-check form-check-inline">
              <input
                id="shadowDiscarded"
                v-model="discarded"
                type="checkbox"
                tabindex="118"
                class="form-check-input"
                @change="setDiscarded(discarded)"
              >
              <label
                class="form-check-label pt-0"
                for="shadowDiscarded"
              >Discarded</label>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="isAdmin"
        class="list-group-item"
      >
        <h4 class="card-title mt-0 mb-2 d-inline-block">
          Debate Status
        </h4>
        <h4 class="text-secondary float-right">
          <small>all debates must be confirmed to complete the round</small>
        </h4>
      </div>
      <div
        v-if="isAdmin"
        class="list-group-item"
      >
        <select
          v-model="status"
          tabindex="119"
          class="form-control"
          @change="setStatus(status)"
        >
          <option value="N">
            none
          </option>
          <option value="D">
            draft
          </option>
          <option value="C">
            confirmed
          </option>
        </select>
      </div>
      <div class="list-group-item">
        <div
          v-if="!isNew && blindEntry && !blindReveal"
          class="row"
          @click="check"
        >
          <button
            tabindex="299"
            class="btn btn-primary btn-block"
            type="button"
          >
            Check Against Draft Ballot
          </button>
        </div>
        <div
          v-if="isNew || !blindEntry || blindReveal"
          class="row"
        >
          <div class="col">
            <button
              tabindex="300"
              :disabled="canSubmit !== '' || !blindFormIsValid || submitting"
              class="btn btn-block btn-success"
              @click="submit"
            >
              <span v-if="isAdmin && !submitting">Save ballot</span>
              <span v-if="!isAdmin && !isNew && !submitting">Confirm draft ballot</span>
              <span v-if="!isAdmin && isNew && !submitting">Add ballot</span>
              <span v-if="submitting">Loading...</span>
            </button>
          </div>
          <div
            v-if="!isNew"
            class="col"
          >
            <button
              tabindex="301"
              class="btn btn-danger btn-block"
              @click="invalidate"
            >
              Reject draft ballot
            </button>
          </div>
        </div>
        <div
          v-if="canSubmit !== ''"
          :disabled="submitting"
          class="text-center pt-3 small text-danger"
        >
          {{ canSubmit }}
        </div>
        <div
          v-if="!isNew && sendReceipts"
          class="text-center pt-3 small text-muted"
        >
          Emails will be sent to adjudicators when the ballot is confirmed.
        </div>
      </div>
    </div>
  </div>
</template>
