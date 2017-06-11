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
      // Data Logic
      if (toDebate === 'unused') {
        var fromPosition = _.findKey(fromDebate.teams, team);
        delete fromDebate.teams[fromPosition]
        this.unallocatedItems.push(team) // Need to push; not append
      }
      if (fromDebate === 'unused') {
        if (toDebate.teams[toPosition]) { // If replacing a team
          this.unallocatedItems.push(toDebate.teams[toPosition])
        }
        toDebate.teams[toPosition] = team
        this.unallocatedItems.splice(this.unallocatedItems.indexOf(team), 1)
      }
      if (toDebate !== 'unused' && fromDebate !== 'unused') {
        var fromPosition = _.findKey(fromDebate.teams, team);
        if (toDebate.teams[toPosition]) { // If replacing a team
          fromDebate.teams[fromPosition] = toDebate.teams[toPosition]
        } else { // If not replacing a team
          delete fromDebate.teams[fromPosition]
        }
        toDebate.teams[toPosition] = team
      }
      // Saving
      var debatesToSave = this.determineDebatesToSave(fromDebate, toDebate)
      this.postModifiedDebates(debatesToSave, 'debate teams of ')
    },
  }
}
</script>