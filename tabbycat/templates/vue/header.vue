<!-- Table Template -->
<script type="text/x-template" id="smart-header">

  <th class="vue-sortable" v-on:click="notifySortByHeader()">

    <span :title="headerData['tooltip']"
          :data-toggle="headerData['tooltip'] ? 'tooltip' : null"
          :v-on:hover="headerData['tooltip'] ? showTooltip  : null">

      <template v-if="headerData['icon']">
        <span class="glyphicon" :class="headerData['icon']"></span>
      </template>

      <template v-if="headerData['visible-sm']">
        <span class="visible-sm-inline">
          [[ headerData['visible-sm'] ]]
        </span>
      </template>

      <template v-if="headerData['visible-md']">
        <span class="visible-md-inline">
          [[ headerData['visible-md'] ]]
        </span>
      </template>

      <template v-if="headerData['visible-lg']">
        <span class="visible-lg-inline">
          [[ headerData['visible-lg'] ]]
        </span>
      </template>

      <template v-if="!headerData.hasOwnProperty('icon') && !headerData.hasOwnProperty('visible-sm') && !headerData.hasOwnProperty('visible-md') && !headerData.hasOwnProperty('visible-lg')">
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
