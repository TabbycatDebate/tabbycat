<template>

  <div class="modal fade" :id="id" tabindex="-1" role="dialog" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4">

          <p class="lead" v-text="gettext(`Auto-Allocate Rooms to Debates`)"></p>
          <p v-text="gettext(`The allocator assigns rooms to debates while trying to match
                              all of the room constraints that have been specified.`)"></p>
          <button type="submit" @click="performWSAction()"
                  :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                  v-text="loading ? gettext('Loading...') : gettext('Auto-Allocate')"></button>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
import ModalActionMixin from '../../templates/modals/ModalActionMixin.vue'

export default {
  mixins: [ModalActionMixin],
  data: function () {
    return {
      id: 'confirmAllocateModal',
    }
  },
}
</script>
