<template>
  <td :class="cellData['class'] ? cellData['class'] : null">

    <span v-if="cellData['sort']" hidden>
      {{ cellData["sort"] }} <!-- Sorting key -->
    </span>

    <!-- Tooltip/Popovers Hovers Wrapper -->
    <popover v-if="canSupportPopover" :cell-data="cellData['popover']">
      <cell-content :cell-data="cellData"></cell-content>
    </popover>

    <template v-if="!canSupportPopover">
      <cell-content :cell-data="cellData"></cell-content>
    </template>

  </td>
</template>

<script>
import CellContent from './CellContent.vue'
import Popover from '../info/Popover.vue'

export default {
  components: { Popover, CellContent },
  props: { cellData: Object },
  computed: {
    canSupportPopover: function () {
      if (typeof this.cellData['popover'] !== 'undefined') {
        if (this.cellData['popover'].hasOwnProperty('content')) {
          return true
        }
      }
      return false
    },
  }
}
</script>
