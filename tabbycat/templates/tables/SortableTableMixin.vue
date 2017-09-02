<script>
// Inheritors should provide a computed property of sortableData
import _ from 'lodash'

export default {
  props: { defaultSortKey: '', defaultSortOrder: '' },
  data: function() {
    // Sort Key/Order need to be internal state; only passed on by
    // the parent for their default values
    return { sortKey: '', sortOrder: '', filterKey: '' }
  },
  created: function() {
    // Set default sort orders and sort keys if they are given
    if (this.defaultSortKey) {
      this.sortKey = this.defaultSortKey
    }
    if (this.defaultSortOrder) {
      this.sortOrder = this.defaultSortOrder
    }
    // Watch for changes in the search box
    this.$eventHub.$on('update-table-filters', this.updateFiltering)
  },
  methods: {
    updateSorting: function(newSortKey) {
      if (this.sortKey === newSortKey) {
        // If sorting by the same key then flip the sort order
        this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc"
      } else {
        this.sortKey = newSortKey
        this.sortOrder = "desc"
      }
    },
    updateFiltering: function(filterKey) {
      this.filterKey = filterKey
    }
  },
  computed: {
    dataOrderedByKey: function() {
      // Find the index of the cell matching the sortKey within each row
      var key = this.sortKey.toLowerCase()
      // Tables with no data have no headers
      if (this.headers.length === 0) {
        return this.sortableData;
      }
      // Identify header matching to sort key
      var orderedHeaderIndex = _.findIndex(this.headers, function(header) {
        return header.key.toLowerCase() == key;
      });
      // If no matches found log an error (asynchronously so table will render)
      if (orderedHeaderIndex === -1) {
        var errorDetails = "No sort key '" + key + "' in headers: " + _.map(this.headers, 'key');
        setTimeout(function () { throw new Error(errorDetails); }, 500)
        return this.sortableData
      }
      // Sort the array of rows based on the value of the cell index
      // For DrawContainer row is the debate dictionary
      var self = this
      return _.orderBy(this.sortableData, function(row) {
        var cellData = self.getSortableProperty(row, orderedHeaderIndex)
        if (_.isString(cellData)) {
          return _.lowerCase(cellData)
        } else {
          return cellData
        }
      }, this.sortOrder)
    },
    dataFilteredByKey: function() {
      if (this.filterKey === '') {
        return this.dataOrderedByKey
      }
      var filterKey = this.filterKey
      return _.filter(this.dataOrderedByKey, function(row) {
        // Filter through all rows; within each row check...
        var rowContainsMatch = false
        _.forEach(row, function(cell) {
          // ...and see if  has cells whose text-string contains filterKey
          if (_.includes(_.lowerCase(cell.text), _.lowerCase(filterKey))) {
            rowContainsMatch = true
          }
        })
        return rowContainsMatch
      })
    }
  }
}
</script>
