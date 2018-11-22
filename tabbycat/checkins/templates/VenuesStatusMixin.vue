<script>
import _ from 'lodash'

export default {
  data: function () {
    return {
      venuesFilterByType: null,
      venuesSortByGroup: {
        Category: true, Name: false, Time: false, Priority: false,
      },
    }
  },
  props: {
    venues: Array,
  },
  methods: {
    getToolTipForVenue: function (entity) {
      let tt = entity.name
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
      const events = this.events
      this.venues.forEach((venue) => {
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
      return _.forEach(this.annotatedVenues, venue => venue)
    },
    venuesByCategory: function () {
      const sortedByCategory = _.sortBy(this.entitiesSortedByName, (v) => {
        if (v.categories.length === 0) {
          return 'Uncategorised'
        }
        return v.categories[0].name
      })
      return _.groupBy(sortedByCategory, (v) => {
        if (v.categories.length === 0) {
          return 'Uncategorised'
        }
        return v.categories[0].name
      })
    },
    venuesByPriority: function () {
      return _.groupBy(this.entitiesSortedByName, v => `Priority ${v.priority}`)
    },
  },
}
</script>
