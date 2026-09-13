<script setup>
import { toRef } from 'vue'
import { useSortableHeader } from '../composables/useSortableHeader.js'

const props = defineProps({
  header: Object,
  sortOrder: String,
  sortKey: String,
  sortHistory: Array,
})

const emit = defineEmits(['resort'])

const sortKey = toRef(props, 'sortKey')
const sortOrder = toRef(props, 'sortOrder')
const sortHistory = toRef(props, 'sortHistory')

const { resort, sortClasses, sortPosition, ariaSort } = useSortableHeader({ sortKey, sortOrder, sortHistory, emit })

const showTooltip = (event) => {
  window.$?.(event.target).tooltip('show')
}

const headerLabel = (header) => {
  return String(header.title || header.tooltip || header.key).replace(/<[^>]*>?/g, ' ')
}
</script>

<template>
  <th
    :class="['vue-sortable', 'sort-' + header.key]"
    :title="header.tooltip"
    :data-toggle="header.tooltip ? 'tooltip' : null"
    :aria-sort="ariaSort(header.key)"
    @hover="header.tooltip ? showTooltip : null"
  >
    <button
      type="button"
      class="vue-sort-button d-flex align-items-end"
      :aria-label="header.icon && !header.text ? headerLabel(header) : null"
      @click="resort(header.key, $event)"
    >
      <i
        v-if="header.icon"
        :data-feather="header.icon"
        :class="['header-icon', header.tooltip ? 'tooltip-trigger' : '']"
        aria-hidden="true"
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
        <i data-feather="chevrons-down" aria-hidden="true" />
        <i data-feather="chevrons-up" aria-hidden="true" />
        <span
          v-if="sortHistory.length > 1 && sortPosition(header.key)"
          class="vue-sort-position"
        >{{ sortPosition(header.key) }}</span>
      </div>
    </button>
  </th>
</template>
