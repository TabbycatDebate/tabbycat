<!-- Table Template -->
<script type="text/x-template" id="smart-header">

  <th class="vue-sortable" v-on:click="notifySortByHeader()"
      v-bind:class="{'vue-sort-active': sortIndex == headerIndex}">

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

    <span class="glyphicon vue-sort-key pull-right"
          :class="sortIndex === headerIndex && sortOrder > 0 ? 'glyphicon-sort-by-attributes' : 'glyphicon-sort-by-attributes-alt'">
    </span>

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
