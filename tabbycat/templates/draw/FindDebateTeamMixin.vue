<script>
import _ from 'lodash'

export default {
  // This is shared between both Debate.vue and EditMachupsContaier.vue
  methods: {
    findDebateTeamInDebateBySide (side, debate) {
      const debateTeam = _.find(debate.debateTeams, dt => dt.side === side)
      if (!_.isUndefined(debateTeam)) {
        return debateTeam
      }
      return false
    },
    findTeamInDebateBySide (side, debate) {
      const find = this.findDebateTeamInDebateBySide(side, debate)
      if (find !== false && find.team !== null) {
        return find.team
      }
      return false
    },
    findDebateTeamInDebateByTeam (team, debate) {
      const debateTeam = _.find(debate.debateTeams, (dt) => {
        if (dt.team !== null) {
          return dt.team.id === team.id
        }
        return false
      })
      return debateTeam
    },
  },
}
</script>
