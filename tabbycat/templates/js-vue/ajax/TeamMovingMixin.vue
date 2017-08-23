<script>
import MovingMixin from '../ajax/MovingMixin.vue'
import _ from 'lodash'

export default {
  mixins: [MovingMixin],
  methods: {
    debateCheckIfShouldSave(debate) {
      var expectedTeams = this.roundInfo.positions.length
      var hasEnoughTeams = _.keys(debate.teams).length === expectedTeams
      return hasEnoughTeams
    },
    saveMoveForType(teamId, fromDebate, toDebate, toPosition) {
      var team = this.allTeamsById[teamId]

      if (toDebate !== 'unused' && fromDebate !== 'unused') {

        // Moving from one debate to another
        var fromPosition = _.findKey(fromDebate.teams, team);
        if (toDebate.teams[toPosition]) {
          // Replacing a team
          fromDebate.teams[fromPosition] = toDebate.teams[toPosition]
        } else {
          // If not replacing a team
          delete fromDebate.teams[fromPosition]
          // Update front end otherwise teams wont appear removed
          this.$set(this.debatesById[fromDebate.id], 'teams', fromDebate.teams)
        }
        // Set the move and update the front end
        toDebate.teams[toPosition] = team
        this.$set(this.debatesById[toDebate.id], 'teams', toDebate.teams)

      } else if (toDebate === 'unused') {

        // Moving to the unused area
        var fromPosition = _.findKey(fromDebate.teams, team);
        delete fromDebate.teams[fromPosition]
        this.unallocatedItems.push(team) // Need to push; not append
        // Update front end otherwise teams wont appear removed
        this.$set(this.debatesById[fromDebate.id], 'teams', fromDebate.teams)

      } else if (fromDebate === 'unused') {

        // Moving to a debate
        if (toDebate.teams[toPosition]) {
          // If replacing a team move them to unused
          this.unallocatedItems.push(toDebate.teams[toPosition])
        }
        // Set the move and update the front end
        toDebate.teams[toPosition] = team
        this.$set(this.debatesById[toDebate.id], 'teams', toDebate.teams)
        // Remove from unallocated
        this.unallocatedItems.splice(this.unallocatedItems.indexOf(team), 1)

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
