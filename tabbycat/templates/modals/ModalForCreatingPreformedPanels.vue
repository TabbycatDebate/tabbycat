<template>

  <div class="modal fade" :id="id" tabindex="-1" role="dialog" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4">

          <p class="lead" v-text="gettext(`Create Preformed Panels`)"></p>
          <p v-text="gettext(`Create preformed panels by estimating the general brackets that will
                              occur during this round.`)"></p>
          <button type="submit" @click="performWSAction()"
                  :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                  v-text="loading ? gettext('Loading...') : gettext('Create Preformed Panels')">
          </button>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
import ModalActionMixin from './ModalActionMixin.vue'

export default {
  mixins: [ModalActionMixin],
  props: { introText: String },
  data: function () {
    // Internal state storing the status of which diversity highlight is being toggled
    return {
      id: 'confirmCreatePreformedPanelsModal',
    }
  },
}
</script>
