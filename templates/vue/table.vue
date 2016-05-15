<!-- Table Template -->
<script type="text/x-template" id="smart-table">

  <table class="table">

    <thead>

      <tr>
        <th v-for="key in gridColumns" @click="sortBy(key)" class="vue-sortable" :class="{vue-sort-active: sortKey == key}">
          [[ key | capitalize ]]
          <span class="glyphicon vue-sort-key pull-right"
            :class="sortOrders[key] > 0 ? 'glyphicon-sort-by-attributes' : 'glyphicon-sort-by-attributes-alt'">
          </span>
        </th>
      </tr>

    </thead>
    <tbody>

      <tr v-for="entry in data | filterBy filterKey | orderBy sortKey sortOrders[sortKey]" >
        <td v-for="key in gridColumns">
          <span v-html="getPrintKey(entry[key])"></span>
        </td>
      </tr>

    </tbody>
  </table>

</script>

<!-- Table Component Behaviour -->
<script>
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
        var firstRow = this.data[0];
        var columns = Object.keys(firstRow);
        return columns
      },
      sortBy: function (key) {
        this.sortKey = key
        this.sortOrders[key] = this.sortOrders[key] * -1
      },
      getPrintKey: function(key) {
        if (key === true) {
          return '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>';
        } else if (key === false) {
          return '<span class="glyphicon glyphicon-remove" aria-hidden="false"></span>';
        } else if (key === "Won") {
          return '<span class="glyphicon glyphicon-arrow-up text-success"></span>';
        } else if (key === "Lost") {
          return '<span class="glyphicon glyphicon-arrow-down text-danger"></span>';
        } else if (key[0] === "/") {
          return '<a href="' + key + '">View</a>'
        } else {
          return key;
        }
      }
    },
    computed: {
      gridColumns: function() {
        return this.getColumns();
      }
    }
  })
</script>
