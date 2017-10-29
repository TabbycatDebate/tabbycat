<template>

  <div class="draw-cell">
    <div class="mt-1 ml-2">

      <label class="custom-control custom-checkbox m-0">
        <input type="checkbox" class="custom-control-input"
               v-model="debate.sidesConfirmed" @click="checkUpdate">
        <span class="custom-control-indicator"></span>
        <span :class="['custom-control-description', debate.sidesConfirmed ? 'text-success' : 'text-danger']">
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
      this.$nextTick(function () { // Wait to model/DOM to catch up
        var sidesStatus = this.debate.sidesConfirmed
        var message = "debate " + this.debate.id + "'s sides as " + sidesStatus
        var payload = { 'sidesStatus': sidesStatus, id: this.debate.id }
        this.ajaxSave(this.saveUrl, payload, message, null, null, null)
      })
    },
  },
}

</script>