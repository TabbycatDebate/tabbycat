<script>
import AjaxMixin from '../ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  methods: {
    saveMove(teamId, fromDebateId, toDebateId, toPosition=null, dontPushToUnused=false, isSwap=false) {
      var team = this.allTeamsById[teamId]
      var toDebate = this.debatesById[toDebateId]
      var fromDebate = this.debatesById[fromDebateId]

      if (_.isUndefined(fromDebate)) { // Undefined if coming from unused
        var from = 'unused'
      } else {
        var from = fromDebate.id
      }
      if (_.isUndefined(toDebate)) { // Undefined if going to unused
        var to = 'unused'
      } else {
        var to = toDebate.id
      }

      if (to === 'unused') {
        var fromPosition = _.findKey(fromDebate.teams, team);
        delete fromDebate.teams[fromPosition]
        this.unallocatedItems.push(team) // Need to push; not append
      }
      if (from === 'unused') {
        if (toDebate.teams[toPosition]) {
          // If replacing a team
          this.unallocatedItems.push(toDebate.teams[toPosition])
        }
        toDebate.teams[toPosition] = team
        this.unallocatedItems.splice(this.unallocatedItems.indexOf(team), 1)
      }
      if (to !== 'unused' && from !== 'unused') {
        var fromPosition = _.findKey(fromDebate.teams, team);
        if (toDebate.teams[toPosition]) {
          // If replacing a team
          fromDebate.teams[fromPosition] = toDebate.teams[toPosition]
        } else {
          // If not replacing a team
          delete fromDebate.teams[fromPosition]
        }
        toDebate.teams[toPosition] = team
      }

      var expectedTeams = this.roundInfo.positions.length
      var debatesToSave = []
      if (to !== 'unused' && _.keys(toDebate.teams).length === expectedTeams) {
        debatesToSave.push(toDebate)
      }
      if (from !== 'unused' && _.keys(fromDebate.teams).length === expectedTeams) {
        if (fromDebate !== toDebate) {
          debatesToSave.push(toDebate)
        }
      }
      var self = this
      _.forEach(debatesToSave, function(debateToSave) {
        var message = 'debate teams of ' + self.niceNameForDebate(debateToSave.id)
        self.ajaxSave(self.roundInfo.saveUrl, debateToSave, message, function(dataResponse) {
          // Replace old debate object with new one
          self.debates[self.debates.indexOf(debateToSave)] = dataResponse
        })
      });

    },
  }
}
</script>