<script>
import _ from 'lodash'

export default {
  // This is shared between both Debate.vue and EditMachupsContaier.vue
  methods: {
    findDebateTeamInDebateBySide(side, debate) {
      var debateTeam = _.find(debate.debateTeams, function(dt) {
        return dt.side === side
      });
      if (!_.isUndefined(debateTeam)) {
        return debateTeam
      } else {
        return false
      }
    },
    findTeamInDebateBySide(side, debate) {
      var find = this.findDebateTeamInDebateBySide(side, debate)
      if (find !== false && find.team !== null) {
        return find.team
      } else {
        return false
      }
    },
    findDebateTeamInDebateByTeam(team, debate) {
      var debateTeam = _.find(debate.debateTeams, function(dt) {
        if (dt.team !== null) {
          return dt.team.id === team.id
        } else {
          return false
        }
      });
      return debateTeam
    },
  }
}
</script>
