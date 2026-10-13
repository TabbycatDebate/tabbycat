<script setup>
import { computed, ref } from 'vue'
import FeatherIcon from '../../../templates/components/FeatherIcon.vue'
import { useDjangoI18n } from '../../../templates/composables/useDjangoI18n.js'

const props = defineProps({
  inputName: String,
  retainedFiles: { type: Array, default: () => [] },
})
const { gettext, ngettext, interpolate } = useDjangoI18n()

const input = ref(null)
const files = ref([])
const retained = ref([...props.retainedFiles])
const allFiles = computed(() => [...retained.value, ...files.value])
const dragging = ref(false)
const formatNumber = new Intl.NumberFormat(document.documentElement.lang || undefined)

function fileLabel (file) {
  if (file.id) {
    return interpolate(ngettext('%(filename)s · %(rows)s row', '%(filename)s · %(rows)s rows', file.row_count), {
      filename: file.name, rows: formatNumber.format(file.row_count),
    }, true)
  }
  const size = formatNumber.format(Math.ceil(file.size / 1024))
  return interpolate(gettext('%(filename)s · %(size)s KB'), { filename: file.name, size }, true)
}

function syncFiles () {
  const transfer = new DataTransfer()
  files.value.forEach(file => transfer.items.add(file))
  input.value.files = transfer.files
}

function addFiles (selection) {
  for (const file of selection) {
    const duplicate = files.value.some(other =>
      other.name === file.name && other.size === file.size && other.lastModified === file.lastModified)
    if (!duplicate) files.value.push(file)
  }
  syncFiles()
}

function removeFile (index) {
  if (index < retained.value.length) retained.value.splice(index, 1)
  else files.value.splice(index - retained.value.length, 1)
  syncFiles()
}

function dropFiles (event) {
  dragging.value = false
  addFiles(event.dataTransfer.files)
}
</script>

<template>
  <div>
    <input
      v-for="file in retained"
      :key="file.id"
      type="hidden"
      name="retained_files"
      :value="file.id"
    >
    <input
      ref="input"
      type="file"
      :name="props.inputName"
      accept=".csv,text/csv"
      multiple
      hidden
      @change="addFiles($event.target.files)"
    >
    <button
      type="button"
      class="csv-drop-zone btn btn-block text-left p-4 mb-3"
      :class="{ 'is-dragging': dragging }"
      @click="input.click()"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="dropFiles"
    >
      <span class="d-flex align-items-center flex-wrap">
        <span class="csv-upload-icon text-primary mr-3"><FeatherIcon name="upload" /></span>
        <span class="mr-auto">
          <strong class="d-block">{{ gettext('Drop your CSV files here') }}</strong>
          <span class="text-muted">{{ gettext('or click to choose files from your computer') }}</span>
        </span>
        <span class="btn btn-outline-primary mt-2">{{ gettext('Choose files') }}</span>
      </span>
    </button>
    <section
      v-if="allFiles.length"
      class="card mb-3"
    >
      <div class="card-header d-flex justify-content-between align-items-center">
        <h3 class="h5 mb-0">
          {{ gettext('Files to import') }}
        </h3>
        <button
          type="button"
          class="btn btn-link btn-sm"
          @click="input.click()"
        >
          {{ gettext('Add more files') }}
        </button>
      </div>
      <ul
        class="list-group list-group-flush"
        aria-live="polite"
      >
        <li
          v-for="(file, index) in allFiles"
          :key="file.id || file"
          class="list-group-item d-flex align-items-center justify-content-between"
        >
          <span>{{ fileLabel(file) }}</span>
          <button
            type="button"
            class="btn btn-outline-secondary btn-sm ml-3"
            :aria-label="interpolate(gettext('Remove %(filename)s'), { filename: file.name }, true)"
            @click="removeFile(index)"
          >
            {{ gettext('Remove') }}
          </button>
        </li>
      </ul>
    </section>
  </div>
</template>
