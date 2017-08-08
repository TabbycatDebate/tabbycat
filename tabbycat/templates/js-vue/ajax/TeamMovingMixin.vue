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
        console.log('saving debate with all teams', debate)
        return true
      } else {
        return false
      }
    },
    saveMoveForType(teamId, fromDebate, toDebate, toPosition) {
      var team = this.allTeamsById[teamId]
      var fromDebateTeam = this.findDebateTeamInDebateByTeam(team, fromDebate)
      var toDebateTeam = this.findDebateTeamInDebateBySide(toPosition, toDebate)

      console.log('team', team, 'from', fromDebateTeam, 'to', toPosition)

      // Data Logic
      if (toDebate === 'unused') {
        fromDebateTeam.team = null
        this.unallocatedItems.push(team) // Need to push; not append
        // Update front end otherwise teams wont appear removed
        this.$set(this.debatesById[fromDebate.id], 'debateTeams',
                  fromDebate.debateTeams)
      }

      if (fromDebate === 'unused') {
        if (toDebateTeam.team !== null) {
          this.unallocatedItems.push(toDebateTeam.team) // If replacing a team
        }
        toDebateTeam.team = team
        this.unallocatedItems.splice(this.unallocatedItems.indexOf(team), 1)
      }

      if (toDebate !== 'unused' && fromDebate !== 'unused') {
        if (toDebateTeam.team !== null) {
          fromDebateTeam.team = toDebateTeam.team // If replacing a team (swap)
        } else {
          fromDebateTeam.team = null // If not replacing a team
          console.log('set to null', fromDebateTeam)
          // Update front end otherwise teams wont appear removed
          this.$set(this.debatesById[fromDebate.id], 'debateTeams',
                    fromDebate.debateTeams)
        }
        toDebateTeam.team = team
        console.log('set to new team', toDebateTeam)
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
