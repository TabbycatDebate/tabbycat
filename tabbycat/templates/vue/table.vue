<!-- Table Template -->
<script type="text/x-template" id="smart-table">

  <table class="table">

    <thead>

      <tr>
        <th class="vue-sortable"
            v-for="(headerIndex, headerType) in gridColumns"
            v-on:click="sortBy(headerType)"
            v-bind:class="{'vue-sort-active': sortKey == headerType}">

          <span v-if="typeof data[0][headerIndex]['head'] !== 'object'">
            [[ data[0][headerIndex]['head'] | capitalize ]]
          </span>

          <template v-else>

            <span :title="data[0][headerIndex]['head']['tooltip']"
                  :data-toggle="data[0][headerIndex]['head']['tooltip'] ? 'tooltip' : null"
                  :v-on:hover="data[0][headerIndex]['head']['tooltip'] ? showTooltip  : null">

                <template v-if="data[0][headerIndex]['head']['icon']">
                  <span class="glyphicon" :class="data[0][headerIndex]['head']['icon']"></span>
                </template>

                <template v-if="data[0][headerIndex]['head']['visible-sm']">
                  <span class="visible-sm-inline">
                    [[ data[0][headerIndex]['head']['visible-sm'] ]]
                  </span>
                </template>
                <template v-if="data[0][headerIndex]['head']['visible-md']">
                  <span class="visible-md-inline">
                    [[ data[0][headerIndex]['head']['visible-md'] ]]
                  </span>
                </template>
                <template v-if="data[0][headerIndex]['head']['visible-lg']">
                  <span class="visible-lg-inline">
                    [[ data[0][headerIndex]['head']['visible-lg'] ]]
                  </span>
                </template>

            </span>

          </template>

          <span class="glyphicon vue-sort-key pull-right"
                :class="sortOrders[key] > 0 ? 'glyphicon-sort-by-attributes' : 'glyphicon-sort-by-attributes-alt'">
          </span>

        </th>
      </tr>

    </thead>
    <tbody>
      <tr v-for="row in data | filterBy filterKey | caseInsensitiveOrderBy sortKey sortOrders[sortKey]" >
        <td v-for="(cellIndex, cellType) in gridColumns" :class="getCellClass(row[cellIndex]['cell'])">

          <span v-if="typeof row[cellIndex]['cell'] !== 'object'" v-html="row[cellIndex]['cell']">
          </span>
          <template v-else>

            <!-- Sorting key -->
            <span v-if="row[cellIndex]['cell']['sort']" class="hidden">
              [[ row[cellIndex]['cell']["sort"] ]]
            </span>


            <!-- Tooltip Hovers -->
            <span :title="row[cellIndex]['cell']['tooltip']"
                  :data-toggle="row[cellIndex]['cell']['tooltip'] ? 'tooltip' : null"
                  :v-on:hover="row[cellIndex]['cell']['tooltip'] ? showTooltip  : null">

              <!-- Icons or Emoji -->
              <span v-if="row[cellIndex]['cell']['icon']" class="glyphicon" :class="row[cellIndex]['cell']['icon']">
              </span>
              <span class="emoji" v-if="row[cellIndex]['cell']['emoji']">
                [[ row[cellIndex]['cell']["emoji"] ]]
              </span>

              <!-- Text (with link if needed) -->
              <a v-if="row[cellIndex]['cell']['link']" :href="row[cellIndex]['cell']['link']" >
                <span v-html="row[cellIndex]['cell']['text']"></span>
              </a>
              <span v-else v-html="row[cellIndex]['cell']['text']"></span>

            </span>

          </template>

        </td>
      </tr>

    </tbody>
  </table>

</script>

<!-- Table Component Behaviour -->
<script>

  Vue.filter('caseInsensitiveOrderBy', function (arr, sortKey, reverse) {
    // This is basically a copy of Vue's native orderBy except we are overriding
    // the last part to see if the cell has custom sort attributes
    if (!sortKey) {
      return arr
    }
    var order = (reverse && reverse < 0) ? -1 : 1
    // sort on a copy to avoid mutating original array
    return arr.slice().sort(function (a, b) {
      if (sortKey !== '$key') {
        if (Vue.util.isObject(a) && '$value' in a) a = a.$value
        if (Vue.util.isObject(b) && '$value' in b) b = b.$value
      }
      a = Vue.util.isObject(a) ? Vue.parsers.path.getPath(a, sortKey) : a
      b = Vue.util.isObject(b) ? Vue.parsers.path.getPath(b, sortKey) : b

      // Check if cell has custom sorting
      if (a && b && typeof(a.sort) !== 'undefined') {
        a = a.sort
        b = b.sort
      } else if (a && b && typeof(a.text) !== 'undefined') {
        a = a.text
        b = b.text
      }
      return a === b ? 0 : a > b ? order : -order
    })

  });

  Vue.component('smart-table', {
    template: '#smart-table',
    props: {
      data: Array,
      columns: Array,
      filterKey: String,
      defaultSortKey: String
    },
    data: function () {
      var sortOrders = {}
      this.getColumns().forEach(function (key) {
        sortOrders[key] = 1; // Set all to sort none (1 is +asc, -1 is desc)
      })
      return {
        sortKey: this.defaultSortKey,
        sortOrders: sortOrders
      }
    },
    methods: {
      getColumns: function() {
        // Extract column headers from first row of data
        var columns = [];
        var firstRow = this.data[0];
        for (var i = 0; i < firstRow.length; i++) {
          // If the header is plain text append it; if a dict then extract the key
          if (typeof(firstRow[i]['head'].key) !== 'undefined') {
            columns.push(firstRow[i]['head'].key)
          } else {
            columns.push(firstRow[i]['head'])
          }
        }
        console.log(columns)
        return columns
      },
      getCellClass: function(cell) {
        if (cell && typeof(cell['cell-class']) !== 'undefined') {
          cell['cell-class']
        } else {
          return null
        }
      },
      sortBy: function (key) {
        // Set the current sorting key; flip it (x * -1) if already in place
        this.sortKey = key
        this.sortOrders[key] = this.sortOrders[key] * -1
      },
      showTooltip: function(event) {
        $(event.target).tooltip('show')
      }
    },
    computed: {
      gridColumns: function() {
        return this.getColumns();
      }
    }
  })
</script>
