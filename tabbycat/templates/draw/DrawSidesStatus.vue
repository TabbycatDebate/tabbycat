<template>

  <div class="draw-cell">
    <div class="mt-1 ml-2">

      <label class="form-check-label m-0 pl-3">
        <input type="checkbox" class="form-check-input"
               v-model.boolean.lazy="debate.sidesConfirmed" @change="checkUpdate">
        <span :class="[debate.sidesConfirmed ? 'text-success' : 'text-danger']">
          <span v-if="!debate.sidesConfirmed">un</span>confirmed
        </span>
      </label>

    </div>
  </div>

</template>

<script>
import AjaxMixin from '../ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  props: {
    debate: Object,
    saveUrl: String
  },
  methods: {
    checkUpdate: function () {
      var sidesStatus = this.debate.sidesConfirmed
      var message = "debate " + this.debate.id + "'s sides as " + sidesStatus
      var payload = { 'sidesStatus': sidesStatus, id: this.debate.id }
      this.ajaxSave(this.saveUrl, payload, message, null, null, null)
    },
  },
}

</script>