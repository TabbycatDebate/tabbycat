<script>
import _ from 'lodash'

export default {
  data: function() {
    return {
      peopleFilterByType: {
        'Adjudicators': false, 'Speakers': false, 'All': true,
      },
      peopleSortByGroup: {
        'By Institution': true, 'By Name': false, 'By Time': false,
      },
    }
  },
  props: {
    'speakers': Array,
    'adjudicators': Array
  },
  methods: {
    getToolTipForPerson: function(entity) {
      var tt = entity.name + ", a " + entity.type
      if (entity.institution === null) {
        tt += ' of no institutional affiliation'
      } else {
        tt += ' from ' + entity.institution.name
      }
      tt += ' with identifier of ' + entity.identifier
      return tt
    },
  },
  computed: {
    annotatedSpeakers: function() {
      var events = this.events
       _.forEach(this.speakers, function(person) {
        person["status"] = _.find(events, ['identifier', person.identifier])
      })
      return this.speakers
    },
    annotatedAdjudicators: function() {
      var events = this.events
      _.forEach(this.adjudicators, function(person) {
        person["status"] = _.find(events, ['identifier', person.identifier])
      })
      return this.adjudicators
    },
    peopleByType: function() {
      var entities = []
      // Filter by speaker type
      if (this.filterByType['All'] || this.filterByType['Adjudicators']) {
        _.forEach(this.annotatedAdjudicators, function(adjudicator) {
          entities.push(adjudicator)
        })
      }
      if (this.filterByType['All'] || this.filterByType['Speakers']) {
        _.forEach(this.annotatedSpeakers, function(speaker) {
          entities.push(speaker)
        })
      }
      return entities
    },
    peopleByInstitution: function() {
      var sortedByInstitution = _.sortBy(this.entitiesSortedByName, function(p) {
        if (p.institution === null) {
          return "Unaffiliated"
        } else {
          return p.institution.name
        }
      })
      return _.groupBy(sortedByInstitution, function(p) {
        if (p.institution === null) {
          return "Unaffiliated"
        } else {
          return p.institution.name
        }
      })
    },
  }
}
</script>