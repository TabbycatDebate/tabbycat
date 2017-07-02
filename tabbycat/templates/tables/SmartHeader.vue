<template>
  <th class="vue-sortable" @click="resort()">

    <span :title="header['tooltip']"
          :data-toggle="header['tooltip'] ? 'tooltip' : null"
          @hover="header['tooltip'] ? showTooltip  : null">

      <span v-if="header['icon']" class="glyphicon" :class="header['icon']"></span>
      <span v-if="header['text']" v-html="header['text']"></span>

      <span v-if="!header.hasOwnProperty('icon') && !header.hasOwnProperty('text')">
        <span>{{ header['key'] }}</span>
      </span>

    </span>

    <span class="glyphicon vue-sort-key" :class="sortClasses"></span>

  </th>
</template>

<script>
import SortableHeaderMixin from '../tables/SortableHeaderMixin.vue'

export default {
  mixins: [SortableHeaderMixin],
  methods: {
    showTooltip: function(event) {
      $(event.target).tooltip('show')
    },
  },
}
</script>
