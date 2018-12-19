<template>
  <div class="card mt-3">
    <div class="card-body">
      <button v-if="isNew" tabindex="299" :disabled="canSubmit !== '' || submitting" @click="submit"
              class="btn btn-block btn-success">
        <span v-if="!submitting">Save draft results</span>
        <span v-if="submitting">Loading...</span>
      </button>
      <div v-if="!isNew" class="row">
        <div class="col">
          <button tabindex="300" :disabled="canSubmit !== '' || submitting" @click="submit"
                  class="btn btn-block btn-success">
            <span v-if="!submitting">Confirm results</span>
            <span v-if="submitting">Loading...</span>
          </button>
        </div>
        <div class="col">
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
</template>

<script>
export default {
  props: {
    isNew: Boolean,
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
