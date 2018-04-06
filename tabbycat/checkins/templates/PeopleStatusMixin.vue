<script>
import _ from 'lodash'

export default {
  data: function () {
    return {
      peopleFilterByType: {
        'Adjudicators': false, 'Debaters': false, 'All': true,
      },
      peopleSortByGroup: {
        'By Institution': true, 'By Name': false, 'By Time': false,
      },
      speakerGroupings: {
        'Show Speakers': false, 'Show Teams': true,
      },
    }
  },
  props: {
    'speakers': Array,
    'adjudicators': Array
  },
  methods: {
    getToolTipForPerson: function (entity) {
      var tt = entity.name + ", a " + entity.type
      if (entity.institution === null) {
        tt += ' of no institutional affiliation'
      } else {
        tt += ' from ' + entity.institution.name
      }
      if (entity.speakers !== null) {
        tt += ' with speakers '
        _.forEach(entity.speakers, function (speaker) {
          var status = speaker.status ? 'Present; id=' : 'Absent; id='
          tt += speaker.name + ' (' + status + ' ' + speaker.identifier[0] + ') '
        })
      } else {
        tt += ' with identifier of ' + entity.identifier[0]
      }
      return tt
    },
    annotatePeople: function (peopleType) {
      var events = this.events
      _.forEach(this[peopleType], function (person) {
        person["status"] = _.find(events, ['identifier', person.identifier[0]])
        if (_.isUndefined(person["status"])) {
          person["status"] = false
        }
      })
      return this[peopleType]
    }
  },
  computed: {
    annotatedSpeakers: function () {
      return this.annotatePeople('speakers')
    },
    annotatedTeams: function () {
      var teams = []
      var groupedSpeakers = _.groupBy(this.annotatedSpeakers, 'team')
      _.forEach(groupedSpeakers, function (teamSpeakers, teamName) {
        var team = {
          'name': teamName, 'id': teamName, 'locked': false, 'type': 'Team',
          'speakers': teamSpeakers, 'institution': teamSpeakers[0].institution,
          'identifier': _.flatten(_.map(teamSpeakers, 'identifier'))
        }
        // Show as green if everyone in
        if (_.filter(team.speakers, ['status', false]).length > 0) {
          team['status'] = false
        } else {
          var lastCheckedIn = _.sortBy(team.speakers, [function (speaker) {
            return speaker.status.time
          }]);
          team['status'] = { 'time': lastCheckedIn[0].status.time }
        }
        teams.push(team)
      })
      return teams
    },
    annotatedDebaters: function () {
      if (this.speakerGroupings['Show Speakers']) {
        return this.annotatedSpeakers
      } else {
        return this.annotatedTeams
      }
    },
    annotatedAdjudicators: function () {
      return this.annotatePeople('adjudicators')
    },
    peopleByType: function () {
      var entities = []
      if (this.filterByType['All'] || this.filterByType['Adjudicators']) {
        _.forEach(this.annotatedAdjudicators, function (adjudicator) {
          entities.push(adjudicator)
        })
      }
      if (this.filterByType['All'] || this.filterByType['Debaters']) {
        _.forEach(this.annotatedDebaters, function (speakerOrTeam) {
          entities.push(speakerOrTeam)
        })
      }
      return entities
    },
    peopleByInstitution: function () {
      var sortedByInstitution = _.sortBy(this.entitiesSortedByName, function (p) {
        if (p.institution === null) {
          return "Unaffiliated"
        } else {
          return p.institution.code
        }
      })
      return _.groupBy(sortedByInstitution, function (p) {
        if (p.institution === null) {
          return "Unaffiliated"
        } else {
          return p.institution.code
        }
      })
    },
  }
}
</script>