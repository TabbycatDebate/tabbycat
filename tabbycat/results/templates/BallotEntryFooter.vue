<template>
  <div class="card mt-3">
    <div class="list-group list-group-flush">
      <div v-if="isAdmin" class="list-group-item">
        <h4 class="card-title mt-0 mb-2 d-inline-block">Ballot Status</h4>
        <h4 class="text-secondary float-right">
          <small>only the confirmed ballot set will affect this debate's result</small>
        </h4>
      </div>
      <div v-if="isAdmin" class="list-group-item">
        <div class="row">
          <div class="col-lg-2 pt-1">
            <div class="form-check form-check-inline">
              <input type="checkbox" id="shadowConfirmed" tabindex="117" class="form-check-input"
                     @change="setConfirmed(confirmed)" v-model="confirmed">
              <label class="form-check-label pt-0" for="shadowConfirmed">Confirmed</label>
            </div>
          </div>
          <div class="col-lg-2 pt-1">
            <div class="form-check form-check-inline">
              <input type="checkbox" id="shadowDiscarded" tabindex="118" class="form-check-input"
                     @change="setDiscarded(discarded)" v-model="discarded">
              <label class="form-check-label pt-0" for="shadowDiscarded">Discarded</label>
            </div>
          </div>
        </div>
      </div>
      <div v-if="isAdmin" class="list-group-item">
        <h4 class="card-title mt-0 mb-2 d-inline-block">Debate Status</h4>
        <h4 class="text-secondary float-right">
          <small>all debates must be confirmed to complete the round</small>
        </h4>
      </div>
      <div v-if="isAdmin" class="list-group-item">
        <select v-model="status" @change="setStatus(status)" tabindex="119" class="form-control">
          <option value="N">none</option>
          <option value="D">draft</option>
          <option value="C">confirmed</option>
        </select>
      </div>
      <div class="list-group-item">
        <div v-if="!isNew && blindEntry && !blindReveal" class="row" @click="check">
          <button tabindex="299" class="btn btn-primary btn-block" type="button">
            Check Against Draft Ballot
          </button>
        </div>
        <div v-if="isNew || !blindEntry || blindReveal" class="row">
          <div class="col">
            <button tabindex="300" :disabled="canSubmit !== '' || !blindFormIsValid || submitting"
                    @click="submit" class="btn btn-block btn-success">
              <span v-if="isAdmin && !submitting">Save ballot</span>
              <span v-if="!isAdmin && !isNew && !submitting">Confirm draft ballot</span>
              <span v-if="!isAdmin && isNew && !submitting">Add ballot</span>
              <span v-if="submitting">Loading...</span>
            </button>
          </div>
          <div v-if="!isNew" class="col">
            <button tabindex="301" @click="invalidate" class="btn btn-danger btn-block">
              Reject draft ballot
            </button>
          </div>
        </div>
        <div v-if="canSubmit !== ''" :disabled="submitting" class="text-center pt-3 small text-danger">
          {{ canSubmit }}
        </div>
        <div v-if="!isNew && sendReceipts" class="text-center pt-3 small text-muted">
          Emails will be sent to adjudicators when the ballot is confirmed.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
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
  },
  data: function () {
    return {
      status: this.currentStatus,
      submitting: false,
      confirmed: this.isConfirmed,
      discarded: this.isDiscarded,
    }
  },
  methods: {
    setStatus: function (state) {
      document.getElementById('id_debate_result_status').value = state
    },
    setConfirmed: function (state) {
      document.getElementById('id_confirmed').value = state ? 'True' : 'False'
    },
    setDiscarded: function (state) {
      document.getElementById('id_discarded').value = state ? 'True' : 'False'
    },
    submit: function () {
      this.submitting = true
      document.getElementById('resultsForm').submit()
    },
    check: function () {
      this.$emit('reveal-blind-check', {})
    },
    invalidate: function () {
      this.setStatus(this.totalBallotsubs > 1 ? 'D' : 'N')
      this.setConfirmed(false)
      this.setDiscarded(true)
      this.submit()
    },
  },
}
</script>
