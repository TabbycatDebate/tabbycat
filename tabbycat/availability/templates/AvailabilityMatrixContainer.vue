<script setup>
import { onBeforeUnmount, onMounted, provide, ref } from 'vue'
import AutoSaveCounter from '../../templates/allocations/AutoSaveCounter.vue'
import TablesContainer from '../../templates/tables/TablesContainer.vue'
import { useAjax } from '../../templates/composables/useAjax.js'
import { createAvailabilityQueue } from './availabilityQueue.js'

const props = defineProps({ tablesData: Array })
const lastSaved = ref(null)
const drag = { checked: null }
provide('checkboxDrag', drag)

const { ajaxSave } = useAjax()
const queue = createAvailabilityQueue(
  props.tablesData.flatMap(table => table.data.flat()).filter(cell => cell.dragSelect),
  (url, changes) => new Promise((resolve, reject) => {
    ajaxSave(url, { changes }, 'availability changes', resolve, reject, null)
  }),
  () => { lastSaved.value = null },
  () => { lastSaved.value = new Date() },
)

const endDrag = () => { drag.checked = null }
onMounted(() => {
  window.addEventListener('mouseup', endDrag)
  window.addEventListener('blur', endDrag)
})
onBeforeUnmount(() => {
  window.removeEventListener('mouseup', endDrag)
  window.removeEventListener('blur', endDrag)
})
</script>

<template>
  <div>
    <auto-save-counter
      :last-saved="lastSaved"
      class="mb-3"
    />
    <tables-container
      :tables-data="tablesData"
      @toggle-checked="queue.enqueue"
    />
  </div>
</template>
