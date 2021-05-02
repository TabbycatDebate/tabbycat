<script>
import _ from 'lodash'

export default {
  data: function () {
    return {
      peopleFilterByType: {
        All: true, Adjudicators: false, Debaters: false,
      },
      peopleSortByGroup: {
        Institution: !this.teamCodes, Name: this.teamCodes, Time: false,
      },
      speakerGroupings: {
        Speaker: false, Team: true,
      },
    }
  },
  props: {
    speakers: Array,
    adjudicators: Array,
  },
  methods: {
    getToolTipForPerson: function (entity) {
      if (!this.teamCodes && entity.type !== 'Team' && entity.institution === null && entity.identifier !== null) {
        const subs = [entity.name, entity.type, entity.identifier[0]]
        return this.tct('%s, a %s of no institutional affiliation with identifier of %s', subs)
      }
      if (!this.teamCodes && entity.type !== 'Team' && entity.institution === null) {
        const subs = [entity.name, entity.type]
        return this.tct('%s, a %s of no institutional affiliation with no assigned identifier', subs)
      }
      if (!this.teamCodes && entity.type !== 'Team' && entity.identifier !== null) {
        const subs = [entity.name, entity.type, entity.institution.name, entity.identifier[0]]
        return this.tct('%s, a %s from %s with identifier of %s', subs)
      }
      if (!this.teamCodes && entity.type !== 'Team') {
        const subs = [entity.name, entity.type, entity.institution.name]
        return this.tct('%s, a %s from %s with no assigned identifier', subs)
      }
      if (entity.speakers !== null && entity.type === 'Team') {
        const speakers = []
        _.forEach(entity.speakers, (speaker) => {
          if (speaker.status) {
            speakers.push(this.tct('%s (Present; id=%s)', [speaker.name, speaker.identifier[0]]))
          } else {
            speakers.push(this.tct('%s (Absent; id=%s)', [speaker.name, speaker.identifier[0]]))
          }
        })
        return this.tct('%s, a team with speakers %s', [entity.name, speakers.join(', ')])
      }
      return this.tct('%s, a %s', [entity.name, entity.type])
    },
    annotatePeople: function (peopleType) {
      const self = this
      this[peopleType].forEach((person) => {
        person.status = _.find(self.events, ['identifier', person.identifier[0]])
        if (_.isUndefined(person.status)) {
          person.status = false
        }
      })
      return this[peopleType]
    },
  },
  computed: {
    annotatedSpeakers: function () {
      const speakers = this.annotatePeople('speakers')
      if (this.teamCodes) {
        _.forEach(speakers, (speaker) => {
          speaker.institution = { code: this.gettext('Anonymous (due to team codes)'), name: this.gettext('Anon') }
        })
      }
      return speakers
    },
    annotatedTeams: function () {
      const teams = []
      const groupedSpeakers = _.groupBy(this.annotatedSpeakers, 'team')
      _.forEach(groupedSpeakers, (teamSpeakers, teamName) => {
        const institution = teamSpeakers[0].institution
        const team = {
          name: teamName,
          id: teamName,
          locked: false,
          type: 'Team',
          speakers: teamSpeakers,
          speakersIn: teamSpeakers.length - _.filter(teamSpeakers, ['status', false]).length,
          institution: institution,
          identifier: _.flatten(_.map(teamSpeakers, 'identifier')),
        }
        // Show as green if everyone in
        if (_.filter(team.speakers, ['status', false]).length > 0) {
          team.status = false
        } else {
          const lastCheckedIn = _.sortBy(team.speakers, [function (speaker) {
            return speaker.status.time
          }])
          team.status = { time: lastCheckedIn[0].status.time }
        }
        teams.push(team)
      })
      return teams
    },
    annotatedDebaters: function () {
      if (this.speakerGroupings.Speaker) {
        return this.annotatedSpeakers
      }
      return this.annotatedTeams
    },
    annotatedAdjudicators: function () {
      _.forEach(this.adjudicators, (adjudicator) => {
        if (adjudicator.independent) {
          adjudicator.institution = { code: this.gettext('Independent'), name: this.gettext('Independent') }
        }
      })
      return this.annotatePeople('adjudicators')
    },
    peopleByType: function () {
      const entities = []
      if (this.filterByType.All || this.filterByType.Adjudicators) {
        _.forEach(this.annotatedAdjudicators, (adjudicator) => {
          entities.push(adjudicator)
        })
      }
      if (this.filterByType.All || this.filterByType.Debaters) {
        _.forEach(this.annotatedDebaters, (speakerOrTeam) => {
          entities.push(speakerOrTeam)
        })
      }
      return entities
    },
    peopleByInstitution: function () {
      const sortedByInstitution = _.sortBy(this.entitiesSortedByName, (p) => {
        if (p.institution === null) {
          return this.gettext('Unaffiliated')
        }
        return p.institution.code
      })
      return _.groupBy(sortedByInstitution, (p) => {
        if (p.institution === null) {
          return this.gettext('Unaffiliated')
        }
        return p.institution.code
      })
    },
  },
}
</script>
