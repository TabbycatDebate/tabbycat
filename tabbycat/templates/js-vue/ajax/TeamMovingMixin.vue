<script>
import MovingMixin from '../ajax/MovingMixin.vue'
import _ from 'lodash'

export default {
  mixins: [MovingMixin],
  methods: {
    debateCheckIfShouldSave(debate) {
      var presentTeams = _.filter(debate.debateTeams, function(dt) {
        return dt.team !== null;
      })
      if (debate.debateTeams.length === presentTeams.length) {
        return true
      } else {
        return false
      }
    },
    saveMoveForType(teamId, fromDebate, toDebate, toPosition) {
      var team = this.allTeamsById[teamId]
      var fromDebateTeam = this.findDebateTeamInDebateByTeam(team, fromDebate)
      var toDebateTeam = this.findDebateTeamInDebateBySide(toPosition, toDebate)

      if (toDebate !== 'unused' && fromDebate !== 'unused') {
        // Moving from one debate to another
        if (toDebateTeam.team !== null) {
          fromDebateTeam.team = toDebateTeam.team // If replacing a team (swap)
        } else {
          fromDebateTeam.team = null // If not replacing a team
          // Update front end otherwise teams wont appear removed
          this.$set(this.debatesById[fromDebate.id], 'debateTeams',
                    fromDebate.debateTeams)
        }
        toDebateTeam.team = team

      } else if (fromDebate === 'unused') {
        // Moving to a debate
        if (toDebateTeam.team !== null) {
          this.unallocatedItems.push(toDebateTeam.team) // If replacing a team
        }
        toDebateTeam.team = team
        this.unallocatedItems.splice(this.unallocatedItems.indexOf(team), 1)
        this.$set(this.debatesById[toDebate.id], 'debateTeams',
                  toDebate.debateTeams)

      } else if (toDebate === 'unused') {
        // Moving to the unused area
        fromDebateTeam.team = null
        this.unallocatedItems.push(team) // Need to push; not append
        // Update front end otherwise teams wont appear removed
        this.$set(this.debatesById[fromDebate.id], 'debateTeams',
                  fromDebate.debateTeams)
      }

      // Saving
      var debatesToSave = this.determineDebatesToSave(fromDebate, toDebate)
      // Note: Don't care about locking/restoring state for debate teams
      // saving or not saving; so addToUnused/removeFromUnused are blank here
      this.postModifiedDebates(debatesToSave, null, null, null, 'debate teams of ')
    },
  }
}
</script>
