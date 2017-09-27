<template>
  <th class="vue-sortable" @click="resort(header['key'])"
      :title="header['tooltip']"
      :data-toggle="header['tooltip'] ? 'tooltip' : null"
      @hover="header['tooltip'] ? showTooltip  : null">

    <i v-if="header['icon']" :data-feather="header['icon']"
       :class="[header['tooltip'] ? 'tooltip-trigger'  : '']"></i>

    <span v-if="header['text']" v-html="header['text']"
          :class="[header['tooltip'] ? 'tooltip-trigger'  : '']"></span>

    <span v-if="!header.hasOwnProperty('icon') && !header.hasOwnProperty('text')"
          :class="[header['tooltip'] ? 'tooltip-trigger'  : '']">
      <span>{{ header['key'] }}</span>
    </span>

    <div :class="sortClasses(header['key'])">
      <span class="sorting-placeholder-for-width"></span>
      <i data-feather="chevrons-down"></i>
      <i data-feather="chevrons-up"></i>
    </div>

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
