<script setup>
import { ref } from 'vue'
import FeatherIcon from '../../../templates/components/FeatherIcon.vue'
import { useDjangoI18n } from '../../../templates/composables/useDjangoI18n.js'

const props = defineProps({ inputName: String })
const { gettext } = useDjangoI18n()
const input = ref(null)
const files = ref([])
const dragging = ref(false)

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
  files.value.splice(index, 1)
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
      v-if="files.length"
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
          v-for="(file, index) in files"
          :key="index"
          class="list-group-item d-flex align-items-center justify-content-between"
        >
          <span>{{ file.name }} · {{ Math.ceil(file.size / 1024) }} KB</span>
          <button
            type="button"
            class="btn btn-outline-secondary btn-sm ml-3"
            :aria-label="`${gettext('Remove')} ${file.name}`"
            @click="removeFile(index)"
          >
            {{ gettext('Remove') }}
          </button>
        </li>
      </ul>
    </section>
  </div>
</template>
