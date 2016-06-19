<template>

  <table class="table" :class="tableClass">
    <thead>
      <tr>
        <template v-for="(headerIndex, headerData) in headers">
          <smart-header :header-index="headerIndex"
                        :header-data="headerData"
                        :sort-index="sortIndex"
                        :sort-order="sortOrder"></smart-header>
        </template>
      </tr>
    </thead>
    <tbody>
      <tr v-if="typeof tableHeaders === 'undefined'"><td class="h4">No Data Available</td></tr>
      <tr v-for="row in rows | filterBy filterKey | caseInsensitiveOrderBy sortIndex sortOrder" >
        <template v-for="(cellIndex, cellData) in row">
          <smart-cell v-if="!cellData['component']" :cell-data="cellData"></smart-cell>
          <component v-else :is="cellData['component']" :component-data="cellData"></component>
        </template>
      </tr>
    </tbody>
  </table>

</template>

<script>
  import SmartHeader from './Header.vue'
  import SmartCell from './Cell.vue'

  export default {
    template: '#smart-table',
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
      SmartCell
    },
    data: function () {
      return {
        sortIndex: this.getDefaultSortIndex(),
        sortOrder: this.getDefaultSortOrder()
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
        var index = null
        if (typeof(this.tableHeaders) !== 'undefined') { // Check table is not empty
          for (var i = 0; i < this.tableHeaders.length; i++) {
            if (this.defaultSortKey !== "") {
              if (this.tableHeaders[i].key === this.defaultSortKey) {
                index = i
              }
            } else {
              index = 0; // if defaultSortKey is not set
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
