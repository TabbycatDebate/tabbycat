<!-- Table Template -->
<script type="text/x-template" id="smart-table">

  <table class="table">

    <thead>

      <tr>
        <th class="vue-sortable"
            v-for="(headerIndex, header) in headers"
            v-on:click="sortByHeader(headerIndex)"
            v-bind:class="{'vue-sort-active': sortIndex == headerIndex}">

            <span :title="header['tooltip']"
                  :data-toggle="header['tooltip'] ? 'tooltip' : null"
                  :v-on:hover="header['tooltip'] ? showTooltip  : null">

                <template v-if="header['icon']">
                  <span class="glyphicon" :class="header['icon']"></span>
                </template>

                <template v-if="header['visible-sm']">
                  <span class="visible-sm-inline">
                    [[ header['visible-sm'] ]]
                  </span>
                </template>

                <template v-if="header['visible-md']">
                  <span class="visible-md-inline">
                    [[ header['visible-md'] ]]
                  </span>
                </template>

                <template v-if="header['visible-lg']">
                  <span class="visible-lg-inline">
                    [[ header['visible-lg'] ]]
                  </span>
                </template>

                <template v-if="!header.hasOwnProperty('icon') && !header.hasOwnProperty('visible-sm') && !header.hasOwnProperty('visible-md') && !header.hasOwnProperty('visible-lg')">
                  [[ header['key'] ]]
                </template>

            </span>

          </template>

          <span class="glyphicon vue-sort-key pull-right"
                :class="headers[headerIndex].order > 0 ? 'glyphicon-sort-by-attributes' : 'glyphicon-sort-by-attributes-alt'">
          </span>

        </th>
      </tr>

    </thead>
    <tbody>
      <tr v-for="row in rows | filterBy filterKey | caseInsensitiveOrderBy sortIndex headers[sortIndex].order" >
        <td v-for="(cellIndex, cell) in row" :class="cell['cell-class'] ? cell['cell-class'] : null">

            <!-- Sorting key -->
            <span v-if="cell['sort']" class="hidden">
              [[ cell["sort"] ]]
            </span>

            <!-- Tooltip Hovers Wrapper -->
            <span :title="cell['tooltip']"
                  :data-toggle="cell['tooltip'] ? 'tooltip' : null"
                  :v-on:hover="cell['tooltip'] ? showTooltip  : null">

                <!-- Icons or Emoji -->
                <span v-if="cell['icon']" class="glyphicon" :class="cell['icon']">
                </span>
                <span class="emoji" v-if="cell['emoji']">
                  [[ cell["emoji"] ]]
                </span>

                <!-- Text (with link if needed) -->
                <a v-if="cell['link']" :href="cell['link']" >
                  <span v-html="cell['text']"></span>
                </a>
                <span v-else v-html="cell['text']"></span>

            </span>

        </td>
      </tr>

    </tbody>
  </table>

</script>

<!-- Table Component Behaviour -->
<script>

  Vue.filter('caseInsensitiveOrderBy', function (arr, sortIndex, reverse) {
    // This is basically a copy of Vue's native orderBy except we are overriding
    // the last part to see if the cell has custom sort attributes
    if (!sortIndex) {
      return arr
    }

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
    data: function () {
      return {
        sortIndex: this.getDefaultSortIndex(),
      }
    },
    methods: {
      getDefaultSortIndex: function() {
        // Find the index of the column that matches the default sorting key
        var index = null
        for (var i = 0; i < this.tableContent[0].length; i++) {
          if (this.tableContent[0][i]['head'].key === this.defaultSortKey) {
            index = i
          }
        }
        return index
      },
      sortByHeader: function (headerIndex) {
        // Set the current sorting key; flip it (x * -1) if already in place
        // We have to modify the original .data so that the computed props will update
        var originalHeaderOrder = this.tableContent[0][headerIndex]['head'].order
        this.tableContent[0][headerIndex]['head'].order = originalHeaderOrder * -1;
        this.sortIndex = headerIndex;
      },
      showTooltip: function(event) {
        $(event.target).tooltip('show')
      }
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
        var headers = [];
        // For each cell in the rows; push its head value to a consolidated list
        for (var i = 0; i < this.tableContent[0].length; i++) {
          if (typeof(this.tableContent[0][i]['head']['order']) === 'undefined') {
            this.tableContent[0][i]['head']['order'] = 1 // Add ordering value to each header
          }
          headers.push(this.tableContent[0][i]['head'])
        }
        return headers
      },
    }
  })
</script>
