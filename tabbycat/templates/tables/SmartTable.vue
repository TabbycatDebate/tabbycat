<template>
  <div class="table-responsive-md">
    <table class="table" :class="tableClass" >

      <thead>
        <tr>
          <th v-for="header in headers" :key="header.key" @resort="updateSorting"
              :header="header"
              :sort-key="sortKey"
              :sort-order="sortOrder"
              is="smartHeader">
          </th>
        </tr>
      </thead>

      <tbody>
        <tr v-if="typeof tableHeaders === 'undefined' || rows.length === 0">
          <td class="empty-cell text-center text-muted">
            {{ emptyTitle }}
          </td>
        </tr>
        <tr v-for="row in dataFilteredByKey">
          <td v-for="(cellData, cellIndex) in row" :key="cellIndex" :cell-data="cellData"
              :is="cellData['component'] ? cellData['component'] : 'SmartCell'">
          </td>
        </tr>
      </tbody>

    </table>
  </div>
</template>

<script>
import _ from 'lodash'
import SmartHeader from './SmartHeader.vue'
import SmartCell from './SmartCell.vue'
import SortableTableMixin from '../tables/SortableTableMixin.vue'
import CheckCell from '../tables/CheckCell.vue'
import BallotsCell from '../../results/templates/BallotsCell.vue'

export default {
  mixins: [SortableTableMixin],
  components: {
    SmartHeader,
    SmartCell,
    CheckCell,
    BallotsCell,
    FeedbackTrend: () => import('../graphs/FeedbackTrend.vue'),
  },
  props: {
    tableHeaders: Array,
    tableContent: Array,
    tableClass: String,
    emptyTitle: String,
  },
  computed: {
    rows: function () {
      const rows = []
      for (let i = 0; i < this.tableContent.length; i += 1) {
        const rowCells = []
        // For each row and cell type push it to the master list
        for (let j = 0; j < this.tableContent[i].length; j += 1) {
          rowCells.push(this.tableContent[i][j])
        }
        rows.push(rowCells)
      }
      return rows
    },
    headers: function () {
      // For each cell in the rows push its head value to a consolidated list
      const headers = []
      if (typeof (this.tableContent[0]) !== 'undefined') { // Check table is not empty
        for (let i = 0; i < this.tableHeaders.length; i += 1) {
          headers.push(this.tableHeaders[i])
        }
      }
      return headers
    },
    sortableData: function () {
      return this.rows // Enables SortableTableMixin
    },
  },
  methods: {
    getSortableProperty (row, orderedHeaderIndex) {
      const cell = row[orderedHeaderIndex]
      const cellData = _.isUndefined(cell.sort) ? cell.text : cell.sort
      return cellData
    },
  },

}
</script>
