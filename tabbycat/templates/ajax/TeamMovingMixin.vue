<script>
import _ from 'lodash'
import MovingMixin from '../ajax/MovingMixin.vue'

export default {
  mixins: [MovingMixin],
  methods: {
    debateCheckIfShouldSave (debate) {
      const presentTeams = _.filter(debate.debateTeams, dt => dt.team !== null)
      if (presentTeams.length === this.roundInfo.teamPositions.length) {
        return true
      }
      return false
    },
    saveMoveForType (teamId, fromDebate, toDebate, toPosition) {
      const team = this.allTeamsById[teamId]
      const fromDebateTeam = this.findDebateTeamInDebateByTeam(team, fromDebate)
      let toDebateTeam = this.findDebateTeamInDebateBySide(toPosition, toDebate)

      if (toDebateTeam === false && toDebate !== 'unused') {
        // For totally new debates they wont even have the DT; so create it
        if (!_.isUndefined(toDebateTeam)) {
          toDebate.debateTeams.push({ side: toPosition, team: null })
        }
        // And re-calculate the toTeam
        toDebateTeam = this.findDebateTeamInDebateBySide(toPosition, toDebate)
      }

      if (toDebate !== 'unused' && fromDebate !== 'unused') {
        // Moving from one debate to another
        if (toDebateTeam.team !== null) {
          fromDebateTeam.team = toDebateTeam.team // If replacing a team (swap)
        } else {
          fromDebateTeam.team = null // If not replacing a team
        }
        toDebateTeam.team = team
      } else if (fromDebate === 'unused') {
        // Moving to a debate
        if (toDebateTeam.team !== null) {
          this.unallocatedItems.push(toDebateTeam.team) // If replacing a team
        }
        toDebateTeam.team = team
        this.unallocatedItems.splice(this.unallocatedItems.indexOf(team), 1)
      } else if (toDebate === 'unused') {
        // Moving to the unused area
        fromDebateTeam.team = null
        this.unallocatedItems.push(team) // Need to push; not append
      }

      // Update front end otherwise teams wont appear removed
      if (toDebate !== 'unused') {
        this.$set(this.debatesById[toDebate.id], 'debateTeams', toDebate.debateTeams)
      }
      if (fromDebate !== 'unused') {
        this.$set(this.debatesById[fromDebate.id], 'debateTeams', fromDebate.debateTeams)
      }

      // Saving
      const debatesToSave = this.determineDebatesToSave(fromDebate, toDebate)
      // Note: Don't care about locking/restoring state for debate teams
      // saving or not saving; so addToUnused/removeFromUnused are blank here
      this.postModifiedDebates(debatesToSave, null, null, null, 'debate teams of ')
    },
  },
}
</script>
