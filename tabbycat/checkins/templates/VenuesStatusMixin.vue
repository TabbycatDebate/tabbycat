<script>
import _ from 'lodash'

export default {
  data: function() {
    return {
      venuesFilterByType: null,
      venuesSortByGroup: {
        'By Category': true, 'By Name': false, 'By Time': false, 'By Priority': false
      },
    }
  },
  props: {
    'venues': Array
  },
  methods: {
    getToolTipForVenue: function(entity) {
      var tt = entity.name
      if (entity.categories.length > 0) {
        tt += ' ('
        _.forEach(entity.categories, function(c) {
          tt += c.name + '; '
        })
        tt += ') '
      } else {
        tt += ' (no category) '
      }
      tt += ' with identifier of ' + entity.identifier
      return tt
    },
  },
  computed: {
    annotatedVenues: function() {
      var events = this.events
      _.forEach(this.venues, function(venue) {
        venue["status"] = _.find(events, ['identifier', venue.identifier])
        venue["name"] = venue["display_name"] // Match people here
      })
      return this.venues
    },
    venuesByType: function() {
      return _.forEach(this.annotatedVenues, function(venue) {
        return venue
      })
    },
    venuesByCategory: function() {
      var sortedByCategory = _.sortBy(this.entitiesSortedByName, function(v) {
        if (v.categories.length === 0) {
          return "No Categories"
        } else {
          return v.categories[0].name
        }
      })
      return _.groupBy(sortedByCategory, function(v) {
        if (v.categories.length === 0) {
          return "No Categories"
        } else {
          return v.categories[0].name
        }
      })
    },
    venuesByPriority: function() {
      return _.groupBy(this.entitiesSortedByName, function(v) {
        return "Priority " + v.priority
      })
    },
  }
}
</script>