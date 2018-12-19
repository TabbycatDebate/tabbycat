<template>
  <div class="card mt-3">
    <div class="card-body">
      <button v-if="isNew" tabindex="299" :disabled="!canSubmit" class="btn btn-block btn-success">
        Save draft results
      </button>
      <div v-if="!isNew" class="row">
        <div class="col">
          <button tabindex="300" :disabled="!canSubmit"
            :class="['btn btn-block', author === ballotAuthor ? 'btn-danger' : 'btn-success']">
            Confirm results
          </button>
        </div>
        <div class="col">
          <button tabindex="301" class="btn btn-danger btn-block" type="button">
            Results are incorrect
          </button>
        </div>
      </div>
      <div v-if="!isNew && sendReceipts && canSubmit"
           class="text-center pt-3 small text-muted">
        Emails will be sent to adjudicators when the ballot is confirmed.
      </div>
      <div v-if="!canSubmit && isNew" class="text-center pt-3 small text-danger">
        Ballot cannot be confirmed because it contains errors.
      </div>
      <div v-if="!canSubmit && !isNew" class="text-center pt-3 small text-danger">
        Ballot cannot be saved because it contains errors.
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    isNew: Boolean,
    canSubmit: Boolean,
    sendReceipts: Boolean,
  },
}
</script>
