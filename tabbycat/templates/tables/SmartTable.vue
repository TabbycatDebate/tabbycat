<template>
  <table class="table" :class="tableClass">

    <thead>
      <tr>
        <th v-for="header in headers" @resort="updateSorting"
            :header="header"
            :sort-key="sortKey"
            :sort-order="sortOrder"
            is="smartHeader">
        </th>
      </tr>
    </thead>

    <tbody>
      <tr v-if="typeof tableHeaders === 'undefined' || rows.length === 0">
        <td class="empty-cell text-center text-muted">No Data Available</td>
      </tr>
      <tr v-for="row in dataFilteredByKey">
        <td v-for="(cellData, cellIndex) in row"
          :is="cellData['component'] ? cellData['component'] : 'SmartCell'"
          :cell-data="cellData">
        </td>
      </tr>
    </tbody>

  </table>
</template>

<script>
import SmartHeader from './SmartHeader.vue'
import SmartCell from './SmartCell.vue'
import SortableTableMixin from '../tables/SortableTableMixin.vue'
import FeedbackTrend from '../graphs/FeedbackTrend.vue'
import _ from 'lodash'

export default {
  mixins: [SortableTableMixin],
  components: { SmartHeader, SmartCell, FeedbackTrend },
  props: { tableHeaders: Array, tableContent: Array, tableClass: String },
  computed: {
    rows: function() {
      var rows = []
      for (var i = 0; i < this.tableContent.length; i++) {
        // For each row and cell type push it to the master list
        var rowCells = []
        for (var j = 0; j < this.tableContent[i].length; j++) {
          rowCells.push(this.tableContent[i][j]);
        }
        rows.push(rowCells);
      };
      return rows;
    },
    headers: function() {
      // For each cell in the rows push its head value to a consolidated list
      var headers = [];
      if (typeof(this.tableContent[0]) !== 'undefined') { // Check table is not empty
        for (var i = 0; i < this.tableHeaders.length; i++) {
          headers.push(this.tableHeaders[i])
        }
      }
      return headers
    },
    sortableData: function() {
      return this.rows // Enables SortableTableMixin
    },
  },
  methods: {
    getSortableProperty(row, orderedHeaderIndex) {
      var cell = row[orderedHeaderIndex]
      var cellData = _.isUndefined(cell.sort) ? cell.text : cell.sort
      return cellData
    }
  }

}
</script>
