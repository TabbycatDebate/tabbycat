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
        ballot status buttons
      </div>
      <div v-if="isAdmin" class="list-group-item">
        <h4 class="card-title mt-0 mb-2 d-inline-block">Debate Status</h4>
        <h4 class="text-secondary float-right">
          <small>all debates must be confirmed to complete the round</small>
        </h4>
      </div>
      <div v-if="isAdmin" class="list-group-item">
        debate status buttons
      </div>
      <div class="list-group-item">
        <div class="row">
          <div class="col">
            <button tabindex="300" :disabled="canSubmit !== '' || submitting" @click="submit"
                    class="btn btn-block btn-success">
              <span v-if="isAdmin && !submitting">Save ballot</span>
              <span v-if="!isAdmin && !isNew && !submitting">Confirm results</span>
              <span v-if="!isAdmin && isNew && !submitting">Confirm results</span>
              <span v-if="submitting">Loading...</span>
            </button>
          </div>
          <div v-if="!isNew" class="col">
            <button tabindex="301" class="btn btn-danger btn-block" type="button">
              Results are incorrect
            </button>
          </div>
        </div>
        <div v-if="canSubmit !== ''" class="text-center pt-3 small text-danger">
          {{ canSubmit }}
        </div>
        <div v-if="!isNew && sendReceipts"
             class="text-center pt-3 small text-muted">
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
    canSubmit: String,
    sendReceipts: Boolean,
  },
  data: function () {
    return {
      submitting: false,
    }
  },
  methods: {
    submit: function () {
      this.submitting = true
      document.getElementById('resultsForm').submit()
    },
  },
}
</script>
