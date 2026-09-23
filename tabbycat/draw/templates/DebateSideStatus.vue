<script setup>
import { computed } from 'vue'
import { useDragAndDropStore } from '../../templates/allocations/DragAndDropStore.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

const props = defineProps({
  debate: Object,
})

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()

const confirmed = computed(() => {
  const debate = store.allDebatesOrPanels?.[props.debate.id]
  return debate?.sides_confirmed
})

const updateStatus = (e) => {
  const importanceChanges = [{ id: props.debate.id, sides_confirmed: e.target.checked }]
  store.updateDebatesOrPanelsAttribute({ sides_confirmed: importanceChanges })
}
</script>

<template>
  <div :class="['flex-3 flex-truncate d-flex', !confirmed ? 'bg-danger text-white' : '']">
    <div class="align-self-center flex-fill pl-3 ">
      <label class="form-check-label m-0 pl-3 ">
        <input
          type="checkbox"
          class="form-check-input"
          :checked="confirmed"
          @input="updateStatus"
        >
        <span class="hoverable small">{{ confirmed ? gettext('confirmed') : gettext('unconfirmed') }}</span>
      </label>
    </div>
  </div>
</template>
