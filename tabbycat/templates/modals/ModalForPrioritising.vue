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

const id = 'confirmPrioritiseModal'
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
            {{ introText }}
          </p>
          <p>
            {{ gettext(`Prioritise by bracket will split the draw into quartiles by bracket
                              and give higher priorities to higher brackets.`) }}
          </p>
          <p>
            {{ gettext(`Prioritise by liveness assign live rooms to be important,
                              safe rooms (where all teams are guaranteed to break) to be neutral>,
                              and dead rooms (where all teams cannot break) to be meh. This is
                              typically only useful in the very last preliminary rounds, when many
                              teams are ruled out of the break.`) }}
          </p>
          <p>
            {{ gettext(`Note that 'liveness' doesn't factor in special rules other than a
                              strict mathematical break. Be sure to double-check the results`) }}
          </p>

          <button
            type="submit"
            :class="['btn btn-block btn-success', loading ? 'disabled': '']"
            @click="performWSAction({ type: 'bracket'})"
          >
            {{ loading ? gettext('Loading...') : gettext('Assign Automatic Priorities by Bracket') }}
          </button>
          <button
            type="submit"
            :class="['btn btn-block btn-success mt-4', loading ? 'disabled': '']"
            @click="performWSAction({ type: 'liveness'})"
          >
            {{ loading ? gettext('Loading...') : gettext('Assign Automatic Priorities by Liveness') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
