<script setup>
import { computed, inject } from 'vue'
import { useDjangoI18n } from '../../../templates/composables/useDjangoI18n.js'

const props = defineProps({ rowIndex: Number, fileIndex: Number })
const { gettext } = useDjangoI18n()
const { rows, filters, rowStatus } = inject('csvPreviewState')
const row = computed(() => rows[props.rowIndex])
const status = computed(() => rowStatus(row.value))
const visible = computed(() => filters[props.fileIndex] === 'all' || filters[props.fileIndex] === status.value)
const badgeClass = computed(() => ({ skipped: 'badge-secondary', attention: 'badge-warning', ready: 'badge-success' }[status.value]))
const label = computed(() => {
  if (row.value.skipped) return gettext('Skipped')
  if (row.value.invalid) return gettext('Needs attention')
  return row.value.edited ? gettext('Edited — validate to continue') : gettext('Ready')
})
</script>

<template>
  <div
    v-show="visible"
    class="csv-preview-row border-top"
    :data-status="status"
    :class="{ 'text-muted': row.skipped }"
  >
    <div class="csv-row-summary px-3 py-3">
      <div class="csv-skip">
        <label class="mb-0">
          <input
            v-model="row.skipped"
            type="checkbox"
            :name="row.skip_name"
            :aria-label="gettext('Skip this row')"
          >
          <span class="small">{{ gettext('Skip') }}</span>
        </label>
      </div>
      <div class="csv-row-name">
        <strong>{{ row.name || '—' }}</strong>
        <small class="d-block text-muted">{{ row.file }} · {{ gettext('Line') }} {{ row.line }}</small>
      </div>
      <div class="csv-row-related small text-muted">
        {{ row.related }}
      </div>
      <div>
        <span
          class="badge"
          :class="badgeClass"
        >{{ label }}</span>
      </div>
    </div>
    <details
      class="csv-row-editor px-3 pb-3"
      :open="row.invalid && !row.skipped"
    >
      <summary class="small text-primary">
        {{ gettext('Edit row') }}
      </summary>
      <!-- Inert prevents editing skipped rows without omitting their values from the Django POST. -->
      <div
        class="pt-3"
        :inert="row.skipped ? '' : null"
        @change="row.edited = true"
      >
        <slot />
      </div>
    </details>
  </div>
</template>
