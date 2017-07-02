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
    resort: function() {
      // Notify the parent table to all rows by this index
      this.$emit('resort', this.header['key'])
    }
  },
}
</script>
