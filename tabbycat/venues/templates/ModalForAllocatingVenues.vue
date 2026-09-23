<script setup>
import { ref, toRef } from 'vue'
import { useModalAction } from '../../templates/composables/useModalAction.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

const props = defineProps({
  contextOfAction: String,
})

const { gettext } = useDjangoI18n()
const modal = ref(null)
const { loading, performWSAction } = useModalAction({
  modalRef: modal,
  contextOfAction: toRef(props, 'contextOfAction'),
})

const id = 'confirmAllocateModal'
</script>

<template>
  <div
    :id="id"
    ref="modal"
    class="modal fade"
    tabindex="-1"
    role="dialog"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4">
          <p class="lead">
            {{ gettext(`Auto-Allocate Rooms to Debates`) }}
          </p>
          <p>
            {{ gettext(`The allocator assigns rooms to debates while trying to match
                               all of the room constraints that have been specified.`) }}
          </p>
          <button
            type="submit"
            :class="['btn btn-block btn-success', loading ? 'disabled': '']"
            @click="performWSAction()"
          >
            {{ loading ? gettext('Loading...') : gettext('Auto-Allocate') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
