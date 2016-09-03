<template>

  <table class="table" :class="tableClass">
    <thead>
      <tr>
        <th v-for="(headerIndex, headerData) in headers" :header-index="headerIndex"
            :header-data="headerData"
            :sort-index="sortIndex"
            :sort-order="sortOrder"
            is="smartHeader">
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-if="typeof tableHeaders === 'undefined' || rows.length === 0">
        <td class="empty-cell text-center text-muted">No Data Available</td>
      </tr>
      <tr v-for="row in rows | filterBy filterKey | caseInsensitiveOrderBy sortIndex sortOrder">
        <td v-for="(cellIndex, cellData) in row"
          :is="cellData['component'] ? cellData['component'] : 'SmartCell'"
          :cell-data="cellData">
        </td>
      </tr>
    </tbody>
  </table>

</template>

<script>
  import SmartHeader from './Header.vue'
  import SmartCell from './Cell.vue'
  // Items below here should be admin only ideally
  import FeedbackTrend from '../graphs/FeedbackTrend.vue'

  export default {
    props: {
      tableHeaders: Array,
      tableContent: Array,
      filterKey: String,
      defaultSortKey: String,
      defaultSortOrder: String,
      tableClass: String
    },
    components: {
      SmartHeader,
      SmartCell,
      FeedbackTrend,
    },
    data: function () {
      return {
        sortIndex: this.getDefaultSortIndex(),
        sortOrder: this.getDefaultSortOrder()
      }
    },
    filters: {
      caseInsensitiveOrderBy: function (arr, sortIndex, reverse) {
        // This is basically a copy of Vue's native orderBy except we are
        // overriding the last part to see if the cell has custom sorting
        if (sortIndex === null) {
          return arr; // If not set then return default order (can be desirable)
        } else {
          var order = (reverse && reverse < 0) ? -1 : 1;
          return arr.slice().sort(function (a, b) {
            // Check if cell has custom sorting
            if (a[sortIndex] && b[sortIndex] && typeof(a[sortIndex].sort) !== 'undefined') {
              a = a[sortIndex].sort;
              b = b[sortIndex].sort;
            } else if (a[sortIndex] && b[sortIndex] && typeof(a[sortIndex].text) !== 'undefined') {
              a = a[sortIndex].text;
              b = b[sortIndex].text;
            } else {
              console.log('Error sorting; sort key probably doesnt exist for that cell');
            }
            return a === b ? 0 : a > b ? order : -order;
          });
        }
      }
    },
    methods: {
      getDefaultSortOrder: function() {
        if (this.defaultSortOrder === "desc") {
          return -1;
        } else {
          return 1;
        }
      },
      getDefaultSortIndex: function() {
        // Find the index of the column that matches the default sorting key
        var index = null // if no defaultSortKey is set leave as null
        if (typeof(this.tableHeaders) !== 'undefined') { // Check table is not empty
          for (var i = 0; i < this.tableHeaders.length; i++) {
            if (typeof this.tableHeaders[i].key !== 'undefined' && this.defaultSortKey !== "") {
              if (this.tableHeaders[i].key.toLowerCase() === this.defaultSortKey.toLowerCase()) {
                index = i
              }
            }
          }
        }
        return index
      },
    },
    events: {
      receiveSortByHeader: function (headerIndex) {
        // Set the current sorting key; flip it (x * -1) if already in place
        // We have to modify the original .data so that the computed props will update
        if (this.sortIndex === headerIndex) {
          this.sortOrder = this.sortOrder * -1;
        } else {
          this.sortOrder = 1;
        }
        this.sortIndex = headerIndex;
      },
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
    }
  }
</script>
