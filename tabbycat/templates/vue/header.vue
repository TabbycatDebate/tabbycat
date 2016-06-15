<!-- Table Template -->
<script type="text/x-template" id="smart-header">

  <th class="vue-sortable" v-on:click="notifySortByHeader()">

    <span :title="headerData['tooltip']"
          :data-toggle="headerData['tooltip'] ? 'tooltip' : null"
          :v-on:hover="headerData['tooltip'] ? showTooltip  : null">

      <span v-if="headerData['icon']" class="glyphicon" :class="headerData['icon']"></span>
      <span v-if="headerData['text']" v-html="headerData['text']"></span>

      <template v-if="!headerData.hasOwnProperty('icon') && !headerData.hasOwnProperty('text')">
        [[ headerData['key'] ]]
      </template>

    </span>

    <span class="glyphicon vue-sort-key" :class="sortClasses"></span>

  </th>

</script>

<!-- Table Component Behaviour -->
<script>

  // Define the component
  var smartHeader = Vue.extend({
    template: '#smart-header',
    props: {
      headerData: Object,
      headerIndex: Number,
      sortOrder: Number,
      sortIndex: Number
    },
    computed: {
      sortClasses: function() {
        if (this.sortIndex === this.headerIndex && this.sortOrder < 0) {
          classes = "text-success glyphicon-sort-by-attributes-alt";
        } else if (this.sortIndex === this.headerIndex && this.sortOrder > 0) {
          classes = "text-success glyphicon-sort-by-attributes";
        } else {
          classes = "text-muted glyphicon-sort";
        }
        return classes;
      }
    },
    methods: {
      showTooltip: function(event) {
        $(event.target).tooltip('show')
      },
      notifySortByHeader: function () {
        // Notify the parent table to all rows by this index
        this.$dispatch('receiveSortByHeader', this.headerIndex)
      }
    },
  })

</script>
