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
      <tr v-for="row in rowsFilteredByKey">
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
import FeedbackTrend from '../js-vue/graphs/FeedbackTrend.vue'
import _ from 'lodash'

export default {
  components: {
    SmartHeader,
    SmartCell,
    FeedbackTrend,
  },
  props: {
    tableHeaders: Array,
    tableContent: Array,
    tableClass: String,
    defaultSortKey: '',
    defaultSortOrder: ''
  },
  data: function() {
    // Sort Key/Order need to be internal state; only passed on by
    // the parent for their default values
    return { sortKey: '', sortOrder: '', filterKey: '' }
  },
  created: function() {
    // Set default sort orders and sort keys if they are given
    if (this.defaultSortKey) {
      this.sortKey = this.defaultSortKey
    }
    if (this.defaultSortOrder) {
      this.sortOrder = this.defaultSortOrder
    }
    // Watch for changes in the search box
    this.$eventHub.$on('update-table-filters', this.updateFiltering)
  },
  methods: {
    updateSorting: function(newSortKey) {
      if (this.sortKey === newSortKey) {
        // If sorting by the same key then flip the sort order
        this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc"
      } else {
        this.sortKey = newSortKey
        this.sortOrder = "desc"
      }
    },
    updateFiltering: function(filterKey) {
      this.filterKey = filterKey
    }
  },
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
    rowsOrderedByKey: function() {
      // Find the index of the cell matching the sortKey within each row
      var orderedHeaderIndex = _.findIndex(this.headers, {'key': this.sortKey});
      if (orderedHeaderIndex === -1) {
        console.log("Couldn't locate sort key: ", this.sortKey, " in headers", this.headers)
        return this.rows
      }
      // Sort the array of rows based on the value of the cell index
      return _.orderBy(this.rows, function(row) {
        var cell = row[orderedHeaderIndex]
        var cellData = _.isUndefined(cell.sort) ? cell.text : cell.sort
        return _.lowerCase(cellData)
      }, this.sortOrder)
    },
    rowsFilteredByKey: function() {
      if (this.filterKey === '') {
        return this.rowsOrderedByKey
      }
      var filterKey = this.filterKey
      return _.filter(this.rowsOrderedByKey, function(row) {
        // Filter through all rows; within each row check...
        var rowContainsMatch = false
        _.forEach(row, function(cell) {
          // ...and see if  has cells whose text-string contains filterKey
          if (_.includes(_.lowerCase(cell.text), _.lowerCase(filterKey))) {
            rowContainsMatch = true
          }
        })
        return rowContainsMatch
      })
    }
  }
}
</script>
