<!-- Table Template -->
<script type="text/x-template" id="smart-table">

  <table class="table">
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
      <h4 v-if="typeof tableContent[0] === 'undefined'">No Data Available</h4>
      <tr v-for="row in rows | filterBy filterKey | caseInsensitiveOrderBy sortIndex sortOrder" >
        <template v-for="(cellIndex, cellData) in row">
          <smart-cell :cell-data="cellData"></smart-cell>
        </template>
      </tr>
    </tbody>
  </table>

</script>

<!-- Table Component Behaviour -->
<script>

  Vue.filter('caseInsensitiveOrderBy', function (arr, sortIndex, reverse) {
    // This is basically a copy of Vue's native orderBy except we are overriding
    // the last part to see if the cell has custom sort attributes
    var order = (reverse && reverse < 0) ? -1 : 1
    // sort on a copy to avoid mutating original array
    return arr.slice().sort(function (a, b) {
      // Check if cell has custom sorting
      if (a && b && typeof(a[sortIndex].sort) !== 'undefined') {
        a = a[sortIndex].sort
        b = b[sortIndex].sort
      } else if (a && b && typeof(a[sortIndex].text) !== 'undefined') {
        a = a[sortIndex].text
        b = b[sortIndex].text
      }
      return a === b ? 0 : a > b ? order : -order
    })

  });

  Vue.component('smart-table', {
    template: '#smart-table',
    props: {
      tableContent: Array,
      filterKey: String,
      defaultSortKey: String
    },
    components: {
      // Register the child components locally
      'smart-cell': smartCell,
      'smart-header': smartHeader
    },
    data: function () {
      return {
        sortIndex: this.getDefaultSortIndex(),
        sortOrder: 1
      }
    },
    methods: {
      getDefaultSortIndex: function() {
        // Find the index of the column that matches the default sorting key
        var index = null
        if (typeof(this.tableContent[0]) !== 'undefined') { // Check table is not empty
          for (var i = 0; i < this.tableContent[0].length; i++) {
            if (this.defaultSortKey !== "") {
              if (this.tableContent[0][i]['head'].key === this.defaultSortKey) {
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
            rowCells.push(this.tableContent[i][j]['cell']);
          }
          rows.push(rowCells);
        };
        return rows;
      },
      headers: function() {
        // For each cell in the rows push its head value to a consolidated list
        var headers = [];
        if (typeof(this.tableContent[0]) !== 'undefined') { // Check table is not empty
          for (var i = 0; i < this.tableContent[0].length; i++) {
            headers.push(this.tableContent[0][i]['head'])
          }
        }
        return headers
      },
    }
  })
</script>
