<script>
import _ from 'lodash'

export default {
  data: function () {
    return {
      venuesFilterByType: null,
      venuesSortByGroup: {
        'By Category': true, 'By Name': false, 'By Time': false, 'By Priority': false,
      },
    }
  },
  props: {
    venues: Array,
  },
  methods: {
    getToolTipForVenue: function (entity) {
      var tt = entity.name
      if (entity.categories.length > 0) {
        tt += ' ('
        _.forEach(entity.categories, (c) => {
          tt += `${c.name}; `
        })
        tt += ') '
      } else {
        tt += ' (no category) '
      }
      if (entity.identifier !== null) {
        tt += ` with identifier of ${entity.identifier[0]}`
      } else {
        tt += ' with no assigned identifier '
      }
      return tt
    },
  },
  computed: {
    annotatedVenues: function () {
      var events = this.events
      _.forEach(this.venues, (venue) => {
        if (venue.identifier !== null) {
          venue.status = _.find(events, ['identifier', venue.identifier[0]])
        }
        if (_.isUndefined(venue.status)) {
          venue.status = false
        }
        venue.name = venue.display_name // Match people here
      })
      return this.venues
    },
    venuesByType: function () {
      return _.forEach(this.annotatedVenues, (venue) => {
        return venue
      })
    },
    venuesByCategory: function () {
      var sortedByCategory = _.sortBy(this.entitiesSortedByName, (v) => {
        if (v.categories.length === 0) {
          return 'No Categories'
        }
        return v.categories[0].name
      })
      return _.groupBy(sortedByCategory, (v) => {
        if (v.categories.length === 0) {
          return 'No Categories'
        }
        return v.categories[0].name
      })
    },
    venuesByPriority: function () {
      return _.groupBy(this.entitiesSortedByName, (v) => {
        return `Priority ${v.priority}`
      })
    },
  },
}
</script>