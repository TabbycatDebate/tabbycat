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
      const categories = []
      _.forEach(entity.categories, (c) => {
        categories.push(c.name)
      })
      if (entity.categories.length > 0 && entity.identifier !== null) {
        const substitutions = [entity.name, categories.join(', '), entity.identifier[0]]
        return this.tct('%s (%s) with identifier of %s', substitutions)
      }
      if (entity.categories.length === 0 && entity.identifier !== null) {
        const substitutions = [entity.name, entity.identifier[0]]
        return this.tct('%s (no category) with identifier of %s', substitutions)
      }
      if (entity.categories.length > 0) {
        const substitutions = [entity.name, categories.join(', ')]
        return this.tct('%s (%s) with no assigned identifier', substitutions)
      }
      if (entity.categories.length === 0) {
        return this.tct('%s (no category) with no assigned identifier', [entity.name])
      }
      return entity.name
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
          return this.gettext('No Category')
        }
        return v.categories[0].name
      })
      return _.groupBy(sortedByCategory, (v) => {
        if (v.categories.length === 0) {
          return this.gettext('No Category')
        }
        return v.categories[0].name
      })
    },
    venuesByPriority: function () {
      return _.groupBy(this.entitiesSortedByName, v => this.tct('Priority %1', [v.priority]))
    },
  },
}
</script>
