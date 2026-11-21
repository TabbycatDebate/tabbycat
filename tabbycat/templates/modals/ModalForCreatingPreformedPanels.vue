<script setup>
import { computed, ref, toRef } from 'vue'
import { useModalAction } from '../composables/useModalAction.js'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const props = defineProps({
  introText: String,
  contextOfAction: String,
  panelsExist: Boolean,
})

const { gettext } = useDjangoI18n()
const modal = ref(null)
const { loading, performWSAction } = useModalAction({
  modalRef: modal,
  contextOfAction: toRef(props, 'contextOfAction'),
})

const id = 'confirmCreatePreformedPanelsModal'
const actionLabel = computed(() => (props.panelsExist
  ? gettext('Refresh Brackets and Liveness')
  : gettext('Create Preformed Panels')))
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
            {{ actionLabel }}
          </p>
          <p v-if="panelsExist">
            {{ gettext(`Re-estimate the general brackets and liveness of the existing preformed
                              panels using the latest results. Panels keep their adjudicators and
                              priorities, and new panels are added if more debates are expected.`) }}
          </p>
          <p v-else>
            {{ gettext(`Create preformed panels by estimating the general brackets that will
                              occur during this round.`) }}
          </p>
          <button
            type="submit"
            :class="['btn btn-block btn-success', loading ? 'disabled': '']"
            @click="performWSAction()"
          >
            {{ loading ? gettext('Loading...') : actionLabel }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
