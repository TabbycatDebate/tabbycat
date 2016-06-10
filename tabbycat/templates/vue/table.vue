<!-- Table Template -->
<script type="text/x-template" id="smart-table">

  <table class="table">

    <thead>

      <tr>
        <th class="vue-sortable"
          v-for="key in gridColumns"
          v-on:click="sortBy(key)"
          v-bind:class="{ 'vue-sort-active': sortKey == key}"
        >
          [[ key | capitalize ]]
          <span class="glyphicon vue-sort-key pull-right"
            :class="sortOrders[key] > 0 ? 'glyphicon-sort-by-attributes' : 'glyphicon-sort-by-attributes-alt'"
          >
          </span>
        </th>
      </tr>

    </thead>
    <tbody>
      <tr v-for="row in data | filterBy filterKey | caseInsensitiveOrderBy sortKey sortOrders[sortKey]" >
        <td v-for="cellType in gridColumns">

          <span v-if="typeof row[cellType] != 'object'">
            [[ row[cellType] ]]
          </span>
          <template v-else>

            <span class="hidden" v-if="row[cellType]['sort']">
              [[ row[cellType]["sort"] ]]
            </span>

            <template v-if="row[cellType]['tooltip']">
              <span data-toggle="tooltip" :title="row[cellType]['tooltip']">
            </template>

              <span class="emoji" v-if="row[cellType]['emoji']">
                [[ row[cellType]["emoji"] ]]
              </span>
              <a v-if="row[cellType]['link']" :href="row[cellType]['link']" >
                <span v-html="row[cellType]['text']"></span>
              </a>
              <span v-else v-html="row[cellType]['text']"></span>

            <template v-if="row[cellType]['tooltip']">
              </span>
            </template>

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
      if (typeof(a.sort) !== 'undefined') {
        a = a.sort
        b = b.sort
      } else if (typeof(a.text) !== 'undefined') {
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
      filterKey: String
    },
    data: function () {
      var sortOrders = {}
      this.getColumns().forEach(function (key) {
        sortOrders[key] = 1; // Set all to sort none (1 is +asc, -1 is desc)
      })
      return {
        sortKey: '',
        sortOrders: sortOrders
      }
    },
    methods: {
      getColumns: function() {
        // Extract column headers from first row of data
        var firstRow = this.data[0];
        var columns = Object.keys(firstRow);
        return columns
      },
      sortBy: function (key) {
        // Set the current sorting key; flip it (x * -1) if already in place
        this.sortKey = key
        this.sortOrders[key] = this.sortOrders[key] * -1
      },
    },
    computed: {
      gridColumns: function() {
        return this.getColumns();
      }
    }
  })
</script>
