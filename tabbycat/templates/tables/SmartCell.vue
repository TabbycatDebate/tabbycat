<script setup>
import { computed } from 'vue'
import CellContent from './CellContent.vue'
import Popover from './Popover.vue'

const props = defineProps({ cellData: Object })

const canSupportPopover = computed(() => {
  if (typeof props.cellData.popover !== 'undefined') {
    if (Object.prototype.hasOwnProperty.call(props.cellData.popover, 'content')) {
      return true
    }
  }
  return false
})
</script>

<template>
  <td :class="cellData['class'] ? cellData['class'] : null">
    <span
      v-if="cellData['sort']"
      hidden
    >
      {{ cellData["sort"] }} <!-- Sorting key -->
    </span>

    <!-- Tooltip/Popovers Hovers Wrapper -->
    <popover
      v-if="canSupportPopover"
      :cell-data="cellData['popover']"
    >
      <cell-content :cell-data="cellData" />
    </popover>

    <template v-if="!canSupportPopover">
      <cell-content :cell-data="cellData" />
    </template>
  </td>
</template>
