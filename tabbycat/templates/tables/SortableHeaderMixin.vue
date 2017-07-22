<script>
export default {
  props: {
    header: Object,
    sortOrder: String,
    sortKey: String
  },
  methods: {
    resort: function(key) {
      // Notify the parent table to all rows by this index
      this.$emit('resort', key)
    },
    sortClasses: function(key) {
      var baseCSS = "glyphicon vue-sort-key "
      if (this.sortKey === key) {
        if (this.sortOrder === "asc") {
          return baseCSS + "vue-sort-active glyphicon-sort-by-attributes-alt"
        } else {
          return baseCSS + "vue-sort-active glyphicon-sort-by-attributes"
        }
      }
      return baseCSS + "text-muted glyphicon-sort"
    }
  },
}
</script>
