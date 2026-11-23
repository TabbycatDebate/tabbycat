<script setup>
import { computed, ref } from 'vue'
import { useDjangoI18n } from '../../../templates/composables/useDjangoI18n.js'

const props = defineProps({
  initialRows: Array,
  csrfToken: String,
})
const { gettext, interpolate } = useDjangoI18n()

const rows = ref(props.initialRows.map((row, index) => ({ ...row, index })))
const selectedFile = ref('')
const processing = ref(false)

const importError = ref('')
const interruptedMessage = gettext('Import interrupted. Reload the page to see saved progress, then import the pending rows.')

const files = computed(() => [...new Set(rows.value.map(row => row.file))])
const visibleRows = computed(() => rows.value.filter(row =>
  !selectedFile.value || row.file === selectedFile.value))
const completed = computed(() => rows.value.filter(row => !['pending', 'created'].includes(row.status)).length)
const counts = computed(() => Object.fromEntries(
  ['imported', 'pending', 'skipped', 'failed', 'blocked'].map(status => [
    status,
    rows.value.filter(row => status === 'pending' ? ['pending', 'created'].includes(row.status) : row.status === status).length,
  ]),
))

const statusLabel = status => ({
  pending: gettext('Pending'),
  created: gettext('Created — linking references'),
  imported: gettext('Imported'),
  skipped: gettext('Skipped'),
  failed: gettext('Failed'),
  blocked: gettext('Blocked'),
}[status])

async function startImport () {
  processing.value = true
  while (true) {
    const ready = row => {
      const dependencies = row.status === 'created' ? row.link_dependencies : row.dependencies
      return (dependencies || []).every(index => rows.value[index].status !== 'pending')
    }
    const pending = rows.value.filter(row => row.status === 'pending' && ready(row)).sort((a, b) => a.priority - b.priority)
    const row = pending[0] || rows.value.find(row => row.status === 'created' && ready(row))
    if (!row) break
    try {
      const response = await fetch(window.location.href, {
        method: 'POST',
        credentials: 'same-origin',
        body: new URLSearchParams({ row: row.index, status: row.status, csrfmiddlewaretoken: props.csrfToken }),
      })
      const result = await response.json()
      if (!response.ok) {
        importError.value = result.error || interruptedMessage
        break
      }
      row.status = result.status
      row.errors = result.errors
    } catch {
      importError.value = interruptedMessage
      break
    }
  }
  processing.value = false
}
</script>

<template>
  <div>
    <h2 class="h3">
      {{ gettext('Import progress') }}
    </h2>
    <div class="card mb-3">
      <div class="card-body row">
        <div
          v-for="(count, status) in counts"
          :key="status"
          class="col"
        >
          <strong class="h3 d-block">{{ count }}</strong>
          {{ statusLabel(status) }}
        </div>
      </div>
    </div>
    <p>
      {{ gettext('Keep this page open while importing. You can reload the page and continue with the pending rows.') }}
    </p>
    <button
      type="button"
      class="btn btn-primary mb-3"
      :disabled="processing || importError || !counts.pending"
      @click="startImport"
    >
      {{ gettext('Import pending rows') }}
    </button>
    <p
      role="status"
      aria-live="polite"
    >
      {{ interpolate(gettext('%(completed)s / %(total)s rows completed'), { completed, total: rows.length }, true) }}
    </p>
    <progress
      class="w-100 mb-3"
      :max="rows.length"
      :value="completed"
      :aria-label="gettext('Completed import rows')"
    />
    <p
      v-if="importError"
      role="alert"
      class="alert alert-warning"
    >
      {{ importError }}
    </p>
    <div class="d-flex justify-content-end mb-3">
      <label
        class="mr-2 col-form-label"
        for="csv-result-file"
      >{{ gettext('Show file') }}</label>
      <select
        id="csv-result-file"
        v-model="selectedFile"
        class="form-control w-auto"
      >
        <option value="">
          {{ gettext('All files') }}
        </option>
        <option
          v-for="file in files"
          :key="file"
          :value="file"
        >
          {{ file }}
        </option>
      </select>
    </div>
    <div class="table-responsive card mb-3">
      <table class="table table-striped mb-0">
        <thead>
          <tr>
            <th>{{ gettext('File') }}</th>
            <th>{{ gettext('Row') }}</th>
            <th>{{ gettext('Object') }}</th>
            <th>{{ gettext('Status') }}</th>
            <th>{{ gettext('Errors') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in visibleRows"
            :key="row.index"
          >
            <td>{{ row.file }}</td>
            <td>{{ row.line }}</td>
            <td>{{ row.display_name }}</td>
            <td>{{ statusLabel(row.status) }}</td>
            <td>{{ row.errors }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
