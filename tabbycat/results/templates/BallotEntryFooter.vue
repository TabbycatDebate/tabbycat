<template>
  <div class="card mt-3">
    <div class="card-body">
      <button v-if="isNew" class="btn btn-block btn-success">Save draft results</button>
      <div v-if="!isNew" class="row">
        <div class="col">
          <button :class="['btn btn-block', author === ballotAuthor ? 'btn-danger' : 'btn-success']"
                  :disabled="author === ballotAuthor">Confirm results</button>
        </div>
        <div class="col">
          <button class="btn btn-danger btn-block" type="button">Results are incorrect</button>
        </div>
      </div>
      <div v-if="!isNew && sendReceipts && author !== ballotAuthor"
           class="text-center pt-3 small text-muted">
        Emails will be sent to adjudicators when the ballot is confirmed.
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: { isNew: Boolean, sendReceipts: Boolean, author: String, ballotAuthor: String },
}
</script>
