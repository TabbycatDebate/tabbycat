<template>
  <th :class="['vue-sortable', 'sort-' + header.key]" @click="resort(header.key)"
      :title="header.tooltip" :data-toggle="header.tooltip ? 'tooltip' : null"
      @hover="header.tooltip ? showTooltip : null">
    <div class="d-flex align-items-end">

      <i v-if="header.icon" :data-feather="header.icon"
         :class="['header-icon', header.tooltip ? 'tooltip-trigger' : '']"></i>

      <div v-if="header.text" v-html="header.text"
            :class="[header.tooltip ? 'tooltip-trigger' : '']">
      </div>

      <div v-if="!header.hasOwnProperty('icon') && !header.hasOwnProperty('text')"
            :class="[header.tooltip ? 'tooltip-trigger' : '']">
        <span>{{ header.title }}</span>
      </div>

      <div :class="['mr-auto', sortClasses(header['key'])]">
        <i data-feather="chevrons-down"></i>
        <i data-feather="chevrons-up"></i>
      </div>

    </div>
  </th>
</template>

<script>
import SortableHeaderMixin from '../tables/SortableHeaderMixin.vue'

export default {
  mixins: [SortableHeaderMixin],
  methods: {
    showTooltip: function (event) {
      $(event.target).tooltip('show')
    },
  },
}
</script>
