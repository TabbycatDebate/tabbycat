<!-- Table Template -->
<script type="text/x-template" id="smart-table">

  <table class="table">

    <thead>

      <tr>
        <th v-for="rowHeading in gridColumns" @click="sortBy(rowHeading)" class="vue-sortable" :class="{vue-sort-active: sortKey == rowHeading}">
          [[ rowHeading | capitalize ]]
          <span class="glyphicon vue-sort-key pull-right"
            :class="sortOrders[rowHeading] > 0 ? 'glyphicon-sort-by-attributes' : 'glyphicon-sort-by-attributes-alt'">
          </span>
        </th>
      </tr>

    </thead>
    <tbody>

      <tr v-for="cell in data | filterBy filterKey | orderBy sortKey sortOrders[sortKey]" >
        <td v-for="cellType in gridColumns">
          <span v-if="typeof cell[cellType] != 'object'">
            [[ cell[cellType] ]]
          </span>
          <template v-else>
            <span class="hidden" v-if="cell[cellType]['sort']">
              [[ cell[cellType]["sort"] ]]
            </span>
            <template v-if="cell[cellType]['tooltip']">
              <span data-toggle="tooltip" :title="cell[cellType]['tooltip']">
            </template>
              <span class="emoji" v-if="cell[cellType]['emoji']">
                [[ cell[cellType]["emoji"] ]]
              </span>
              <a v-if="cell[cellType]['link']" :href="cell[cellType]['link']" >
                <span v-html="cell[cellType]['text']"></span>
              </a>
              <span v-else v-html="cell[cellType]['text']"></span>
            <template v-if="cell[cellType]['tooltip']">
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
      getSortingKey: function(cell) {
        // Figure out which value to sort by
        if (typeof cell === 'object') {
          if (cell['sort'] !== null) {
            return cell['sort'];
          } else {
            return cell['text'];
          }
        } else {
          return cell;
        }
      },
      getColumns: function() {
        // Extract column headers from first row of data
        var firstRow = this.data[0];
        var columns = Object.keys(firstRow);
        return columns
      },
      sortBy: function (key) {
        // Set the current sorting key; flip it (*1) if already in place
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
