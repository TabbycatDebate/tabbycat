<script setup>
import { computed, provide, reactive, ref, watch } from 'vue'
import FeatherIcon from '../../../templates/components/FeatherIcon.vue'
import { useDjangoI18n } from '../../../templates/composables/useDjangoI18n.js'

const props = defineProps({
  files: Array,
  preview: Boolean,
})
const { gettext, ngettext, interpolate } = useDjangoI18n()
const storageKey = 'csv-active-file:' + window.location.pathname
const rows = reactive(Object.fromEntries(
  props.files.flatMap(file => file.rows.map(row => [row.index, { ...row, edited: false }])),
))
const filters = reactive(Object.fromEntries(props.files.map(file => [file.index, 'all'])))

const firstInvalid = props.files.findIndex(file => file.attention_count || file.rows.some(row => row.invalid && !row.skipped))
const saved = sessionStorage.getItem(storageKey)
const savedIndex = props.files.findIndex(file => String(file.id) === saved)
const active = ref(firstInvalid >= 0 ? firstInvalid : savedIndex >= 0 ? savedIndex : 0)

const rowCount = computed(() => props.files.reduce((sum, file) => sum + file.row_count, 0))
const rowStatus = row => row.skipped ? 'skipped' : row.invalid ? 'attention' : 'ready'
const fileRows = file => file.rows.map(row => rows[row.index])
const attentionCount = file => fileRows(file).filter(row => rowStatus(row) === 'attention').length
const skippedCount = file => fileRows(file).filter(row => row.skipped).length
const visibleRows = file => fileRows(file).filter(row =>
  filters[file.index] === 'all' || rowStatus(row) === filters[file.index])

const fileCountLabel = computed(() => interpolate(ngettext('%s file', '%s files', props.files.length), [props.files.length]))
const attentionLabel = count => interpolate(ngettext('%s row needs attention', '%s rows need attention', count), [count])
const skippedLabel = count => interpolate(ngettext('%s row skipped', '%s rows skipped', count), [count])
const mappedLabel = count => interpolate(ngettext('%s column mapped', '%s columns mapped', count), [count])
const countLabel = count => interpolate(ngettext('%s row', '%s rows', count), [count])

provide('csvPreviewState', { rows, filters, rowStatus })
watch(active, value => sessionStorage.setItem(storageKey, String(props.files[value].id)), { immediate: true })

function skipInvalid (file) {
  fileRows(file).filter(row => row.invalid).forEach(row => { row.skipped = true })
}
</script>

<template>
  <div class="csv-workspace">
    <nav
      class="csv-file-list card mb-3"
      :aria-label="gettext('Uploaded CSV files')"
    >
      <div class="card-header">
        <h2 class="h6 mb-1">
          {{ gettext('Files to import') }}
        </h2>
        <small class="text-muted">{{ fileCountLabel }} · {{ countLabel(rowCount) }}</small>
      </div>
      <div class="list-group list-group-flush">
        <button
          v-for="(file, index) in files"
          :key="file.id"
          type="button"
          class="list-group-item list-group-item-action csv-file-button"
          :aria-controls="`csv-file-${file.index}`"
          :aria-pressed="active === index"
          @click="active = index"
        >
          <span class="d-flex align-items-start">
            <FeatherIcon
              name="file-text"
              class="mr-2 flex-shrink-0"
            />
            <span class="csv-file-label">
              <strong class="d-block">{{ file.name }}</strong>
              <small class="text-muted">{{ file.type_label }} · {{ countLabel(file.row_count) }}</small>
            </span>
          </span>
          <span class="d-block mt-2">
            <template v-if="preview">
              <span
                v-if="attentionCount(file)"
                class="badge badge-warning"
              >{{ attentionLabel(attentionCount(file)) }}</span>
              <span
                v-else
                class="badge badge-success"
              >{{ gettext('Ready') }}</span>
              <span
                v-if="skippedCount(file)"
                class="badge badge-secondary ml-1"
              >{{ skippedLabel(skippedCount(file)) }}</span>
            </template>
            <span
              v-else
              class="badge badge-light"
            >{{ mappedLabel(file.mapped_count) }}</span>
          </span>
        </button>
      </div>
    </nav>
    <div class="csv-file-panels">
      <section
        v-for="(file, index) in files"
        v-show="active === index"
        :id="`csv-file-${file.index}`"
        :key="file.id"
        class="card mb-3"
      >
        <div class="card-header d-flex justify-content-between align-items-center">
          <div>
            <h2 class="h5 mb-1">
              {{ file.type_label }}
            </h2>
            <span class="text-muted">{{ file.name }}</span>
          </div>
          <span class="badge badge-light">{{ countLabel(file.row_count) }}</span>
        </div>
        <div
          v-if="preview"
          class="card-body py-3 d-flex flex-wrap align-items-center justify-content-between"
        >
          <span class="small text-muted">{{ attentionLabel(attentionCount(file)) }} · {{ skippedLabel(skippedCount(file)) }}</span>
          <div class="d-flex align-items-center mt-2 mt-md-0">
            <button
              type="button"
              class="btn btn-outline-secondary btn-sm mr-2 text-nowrap"
              :disabled="!attentionCount(file)"
              @click="skipInvalid(file)"
            >
              {{ gettext('Skip invalid rows') }}
            </button>
            <label
              class="sr-only"
              :for="`csv-filter-${file.index}`"
            >{{ interpolate(gettext('Filter rows in %(filename)s'), { filename: file.name }, true) }}</label>
            <select
              :id="`csv-filter-${file.index}`"
              v-model="filters[file.index]"
              class="form-control form-control-sm w-auto"
            >
              <option value="all">
                {{ gettext('All rows') }}
              </option>
              <option value="attention">
                {{ gettext('Needs attention') }}
              </option>
              <option value="skipped">
                {{ gettext('Skipped') }}
              </option>
            </select>
          </div>
        </div>
        <slot :name="`file-${file.index}`" />
        <p
          v-if="preview && !visibleRows(file).length"
          class="text-muted p-3 mb-0"
        >
          {{ gettext('No rows match this filter.') }}
        </p>
      </section>
      <div
        v-if="files.length > 1"
        class="d-flex justify-content-between mb-3"
      >
        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          :disabled="active === 0"
          @click="active--"
        >
          {{ gettext('Previous file') }}
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          :disabled="active === files.length - 1"
          @click="active++"
        >
          {{ gettext('Next file') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.csv-workspace {
  display: grid;
  grid-template-columns: minmax(210px, 260px) minmax(0, 1fr);
  gap: 1.25rem;
  align-items: start;
}
.csv-file-list {
  position: sticky;
  top: 1rem;
}
.csv-file-list .list-group {
  max-height: 65vh;
  overflow-y: auto;
}
.csv-file-button[aria-pressed=true] {
  border-left: 3px solid #663da0;
  background: #f0ebf6;
}
.csv-file-label {
  min-width: 0;
  overflow-wrap: anywhere;
}
.csv-file-panels {
  min-width: 0;
}
:deep(.csv-mapping-table th), :deep(.csv-mapping-table td) {
  vertical-align: middle;
}
:deep(.csv-mapping-table label) {
  margin-bottom: 0;
}
:deep(.csv-example) {
  max-width: 220px;
  overflow-wrap: anywhere;
  font-size: .875rem;
}
@media (max-width: 991px) {
  .csv-workspace {
    grid-template-columns: 1fr;
  }
  .csv-file-list {
    position: static;
  }
  .csv-file-list .list-group {
    max-height: 240px;
  }
}
</style>
