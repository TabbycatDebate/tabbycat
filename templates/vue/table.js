<!-- Table Template -->
<script type="text/x-template" id="smart-table">
  <table class="table">
    <thead>
      <tr>
        <th v-for="key in columns" @click="sortBy(key)" class="vue-sortable" :class="{vue-sort-active: sortKey == key}">
          [[ key | capitalize ]]
          <span class="glyphicon vue-sort-key pull-right"
            :class="sortOrders[key] > 0 ? 'glyphicon-sort-by-attributes' : 'glyphicon-sort-by-attributes-alt'">
          </span>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="entry in data | filterBy filterKey | orderBy sortKey sortOrders[sortKey]" >
        <td v-for="key in columns">
          <template v-if="entry['rowLink']">
            <a v-bind:href="entry['rowLink']">[[ entry[key] ]]</a>
          </template>
          <template v-else="entry['rowLink']">
            [[ entry[key] ]]
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
      this.columns.forEach(function (key) {
        sortOrders[key] = 1; // Set all to sort none (1 is +asc, -1 is desc)
      })
      return {
        sortKey: '',
        sortOrders: sortOrders
      }
    },
    methods: {
      sortBy: function (key) {
        this.sortKey = key
        this.sortOrders[key] = this.sortOrders[key] * -1
      }
    }
  })
</script>
