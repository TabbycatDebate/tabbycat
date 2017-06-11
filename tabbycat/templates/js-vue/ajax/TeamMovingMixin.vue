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
        console.log(fromDebate.teams)
        fromDebate.teams = _.filter(fromDebate.teams, function(debateTeam) {
          return debateTeam.team !== team
        })
        this.unallocatedItems.push(team) // Need to push; not append
      }

      var message = 'moved team ' + team.short_name + ' from ' + from + ' to ' + to + ' as ' + toPosition
      var payload = { moved_item: team.id, moved_from: from, moved_to: to }
      payload['position'] = toPosition

      // var self = this
      // this.ajaxSave(this.roundInfo.saveUrl, payload, message, function() {
      //   if (to === 'unused') {
      //     self.processMoveToUnusedFromPanel(adjudicator, fromDebate, dontPushToUnused)
      //   } else {
      //     // var toDebateChair = self.getDebateChair(toDebate).id;
      //     // if (from === 'unused') {
      //     //   self.processMoveToPanelFromUnused(adjudicator, toDebate, toPosition)
      //     //   // If being dropped into an occupied chair position move old chair to unused
      //     //   if (toPosition === 'C' && toDebateChair) {
      //     //     self.saveMove(toDebateChair, toDebate.id, 'unused')
      //     //   }
      //     // } else {
      //     //   if (toPosition !== 'C' || !toDebateChair) {
      //     //     // If not being dropped into the chair position; or if the chair position is empty
      //     //     self.processMoveToPanelFromPanel(adjudicator, fromDebate, toDebate, toPosition)
      //     //   } else {
      //     //     // If being moved to a filled chair we always swap with the previous position
      //     //     self.processMoveToCurrentlyFilledChair(adjudicator, fromDebate, toDebate, isSwap)
      //     //   }
      //     // }
      //   }
      // })
    },
  }
}
</script>