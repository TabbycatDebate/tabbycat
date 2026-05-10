<script setup>
import { ref, toRef } from 'vue'
import { useModalAction } from '../composables/useModalAction.js'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const props = defineProps({
  introText: String,
  contextOfAction: String,
})

const { gettext } = useDjangoI18n()
const modal = ref(null)
const { loading, performWSAction } = useModalAction({
  modalRef: modal,
  contextOfAction: toRef(props, 'contextOfAction'),
})

const id = 'confirmCreatePreformedPanelsModal'
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
            {{ gettext(`Create Preformed Panels`) }}
          </p>
          <p>
            {{ gettext(`Create preformed panels by estimating the general brackets that will
                              occur during this round.`) }}
          </p>
          <button
            type="submit"
            :class="['btn btn-block btn-success', loading ? 'disabled': '']"
            @click="performWSAction()"
          >
            {{ loading ? gettext('Loading...') : gettext('Create Preformed Panels') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
