<!-- Table Template -->
<script type="text/x-template" id="smart-table">

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
      <h4 v-if="typeof tableHeaders === 'undefined'">No Data Available</h4>
      <tr v-for="row in rows | filterBy filterKey | caseInsensitiveOrderBy sortIndex sortOrder" >
        <template v-for="(cellIndex, cellData) in row">
          <smart-cell v-if="!cellData['component']" :cell-data="cellData"></smart-cell>
          <template v-else>
            <feedback-trend v-if="cellData['component'] === 'feedback-trend'"
                          :min-score="cellData['min-score']"
                          :max-score="cellData['max-score']"
                          :round-seq="cellData['round-seq']"
                          :graph-data="cellData['data']">
            </feedback-trend>
            <debate-importance v-if="cellData['component'] === 'debate-importance'"
                            :id="cellData['id']"
                            :importance="cellData['importance']"
                            :url="cellData['url']">
            </debate-importance>
          </template>
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

  // Setup base components
  var tableComponents = {
      'smart-cell': smartCell,
      'smart-header': smartHeader,
  }
  // Extend
  for (var i = 0; i < pluginComponents.length; i++) {
    tableComponents[pluginComponents[i].template] = pluginComponents[i].reference
  }

  Vue.component('smart-table', {
    template: '#smart-table',
    props: {
      tableHeaders: Array,
      tableContent: Array,
      filterKey: String,
      defaultSortKey: String,
      tableClass: String
    },
    components: tableComponents,
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
  })
</script>
