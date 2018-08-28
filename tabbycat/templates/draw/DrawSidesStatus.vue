<template>

  <div class="draw-cell">
    <div class="mt-1 ml-2">

      <label class="form-check-label m-0 pl-3">
        <input type="checkbox" class="form-check-input"
               v-model.lazy="debate.sidesConfirmed" @change="checkUpdate">
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
    saveUrl: String,
  },
  methods: {
    checkUpdate: function () {
      const sidesStatus = this.debate.sidesConfirmed
      const message = `debate ${this.debate.id}'s sides as ${sidesStatus}`
      const payload = { sidesStatus: sidesStatus, id: this.debate.id }
      this.ajaxSave(this.saveUrl, payload, message, null, null, null)
    },
  },
}

</script>
