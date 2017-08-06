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
      // Data Logic
      if (toDebate === 'unused') {
        var fromPosition = _.findKey(fromDebate.debateTeams, team);
        delete fromDebate.debateTeams[fromPosition]
        this.unallocatedItems.push(team) // Need to push; not append
        // Update front end otherwise teams wont appear removed
        this.$set(this.debatesById[fromDebate.id], 'teams', fromDebate.debateTeams)
      }
      if (fromDebate === 'unused') {
        if (toDebate.debateTeams[toPosition]) { // If replacing a team
          this.unallocatedItems.push(toDebate.debateTeams[toPosition])
        }
        toDebate.debateTeams[toPosition] = team
        this.unallocatedItems.splice(this.unallocatedItems.indexOf(team), 1)
      }
      if (toDebate !== 'unused' && fromDebate !== 'unused') {
        var fromPosition = _.findKey(fromDebate.debateTeams, team);
        if (toDebate.debateTeams[toPosition]) {
          // If replacing a team
          fromDebate.debateTeams[fromPosition] = toDebate.debateTeams[toPosition]
        } else {
          // If not replacing a team
          delete fromDebate.debateTeams[fromPosition]
          // Update front end otherwise teams wont appear removed
          this.$set(this.debatesById[fromDebate.id], 'teams', fromDebate.debateTeams)
        }
        toDebate.debateTeams[toPosition] = team
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
