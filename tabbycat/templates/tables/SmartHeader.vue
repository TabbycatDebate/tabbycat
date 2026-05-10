<script setup>
import { toRef } from 'vue'
import { useSortableHeader } from '../composables/useSortableHeader.js'

const props = defineProps({
  header: Object,
  sortOrder: String,
  sortKey: String,
})

const emit = defineEmits(['resort'])

const sortKey = toRef(props, 'sortKey')
const sortOrder = toRef(props, 'sortOrder')

const { resort, sortClasses } = useSortableHeader({ sortKey, sortOrder, emit })

const showTooltip = (event) => {
  window.$?.(event.target).tooltip('show')
}
</script>

<template>
  <th
    :class="['vue-sortable', 'sort-' + header.key]"
    :title="header.tooltip"
    :data-toggle="header.tooltip ? 'tooltip' : null"
    @click="resort(header.key)"
    @hover="header.tooltip ? showTooltip : null"
  >
    <div class="d-flex align-items-end">
      <i
        v-if="header.icon"
        :data-feather="header.icon"
        :class="['header-icon', header.tooltip ? 'tooltip-trigger' : '']"
      />

      <div
        v-if="header.text"
        :class="[header.tooltip ? 'tooltip-trigger' : '']"
        v-html="header.text"
      />

      <div
        v-if="!header.hasOwnProperty('icon') && !header.hasOwnProperty('text')"
        :class="[header.tooltip ? 'tooltip-trigger' : '']"
      >
        <span>{{ header.title }}</span>
      </div>

      <div :class="['mr-auto', sortClasses(header['key'])]">
        <i data-feather="chevrons-down" />
        <i data-feather="chevrons-up" />
      </div>
    </div>
  </th>
</template>
