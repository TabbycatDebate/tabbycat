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
      var baseCSS = "vue-sort-key "
      console.log(this.sortKey, key)
      if (this.sortKey.toLowerCase() === key.toLowerCase()) {
        if (this.sortOrder === "asc") {
          return baseCSS + "vue-sort-active sort-by-asc"
        } else {
          return baseCSS + "vue-sort-active sort-by-desc"
        }
      }
      return baseCSS + "text-muted"
    }
  },
}
</script>
