<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import TablesContainer from '../../templates/tables/TablesContainer.vue'
import { useAjax } from '../../templates/composables/useAjax.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { createAvailabilityQueue } from './availabilityQueue.js'

const props = defineProps({ tablesData: Array, canEdit: Boolean })
const { gettext } = useDjangoI18n()
const status = ref(gettext('Changes save automatically.'))

const warnBeforeUnload = (event) => {
  event.preventDefault()
  event.returnValue = true
}

const { ajaxSave } = useAjax()
const queue = createAvailabilityQueue(
  props.tablesData.flatMap(table => table.data.flat()).filter(cell => cell.component === 'check-cell'),
  (url, changes) => new Promise((resolve, reject) => {
    ajaxSave(url, { changes }, gettext('availability changes'), resolve, reject, null)
  }),
  () => {
    status.value = gettext('Saving changes…')
    window.addEventListener('beforeunload', warnBeforeUnload)
  },
  (saved) => {
    status.value = saved ? gettext('All changes saved.') : gettext('Some changes could not be saved.')
    window.removeEventListener('beforeunload', warnBeforeUnload)
  },
)

let navigating = false
const waitForNavigation = async (event) => {
  const saved = queue.whenIdle()
  if (!saved || event.defaultPrevented || event.button !== 0 ||
      event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return

  const link = event.target.closest('a[href]')
  if (!link || (link.target && link.target !== '_self') || link.hasAttribute('download') ||
      link.getAttribute('href').startsWith('#') || !['http:', 'https:'].includes(link.protocol)) return

  event.preventDefault()
  if (navigating) return
  navigating = true
  const success = await saved
  navigating = false
  if (success) window.location.assign(link.href)
}

onMounted(() => {
  document.addEventListener('click', waitForNavigation)
})
onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', warnBeforeUnload)
  document.removeEventListener('click', waitForNavigation)
})
</script>

<template>
  <div>
    <p
      v-if="canEdit"
      class="text-muted"
      role="status"
    >
      {{ status }}
    </p>
    <tables-container
      :tables-data="tablesData"
      @toggle-checked="queue.enqueue"
    />
  </div>
</template>
