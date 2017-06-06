<!-- Table Template -->
<template>
  <th class="vue-sortable" @click="resort()">

    <span :title="header['tooltip']"
          :data-toggle="header['tooltip'] ? 'tooltip' : null"
          :@hover="header['tooltip'] ? showTooltip  : null">

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
export default {
  props: {
    header: Object,
    sortOrder: String,
    sortKey: String
  },
  computed: {
    sortClasses: function() {
      if (this.sortKey === this.header.key) {
        if (this.sortOrder === "asc") {
          return "text-success glyphicon-sort-by-attributes-alt";
        } else {
          return "text-success glyphicon-sort-by-attributes";
        }
      }
      return "text-muted glyphicon-sort";
    }
  },
  methods: {
    showTooltip: function(event) {
      $(event.target).tooltip('show')
    },
    resort: function() {
      // Notify the parent table to all rows by this index
      this.$emit('resort', this.header['key'])
    }
  },
}
</script>
