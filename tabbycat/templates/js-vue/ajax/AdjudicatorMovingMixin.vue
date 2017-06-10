<script>
import AjaxMixin from '../ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  methods: {
    getDebateChair(debate) {
      var potentialChair = _.find(debate.panel, {'position': 'C'})
      if (_.isUndefined(potentialChair)) {
        return false
      } else {
        return potentialChair.adjudicator
      }
    },
    saveMove(adjudicatorId, fromDebateId, toDebateId, toPosition=null, dontPushToUnused=false, isSwap=false) {
      console.log(adjudicatorId, fromDebateId, toDebateId, toPosition)
      var adjudicator = this.allAdjudicatorsById[adjudicatorId]
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

      var message = 'moved adjudicator ' + adjudicator.name + ' from ' + from + ' to ' + to + ' as ' + toPosition
      var payload = { moved_item: adjudicator.id, moved_from: from, moved_to: to }
      payload['position'] = toPosition
      var self = this
      this.ajaxSave(this.roundInfo.saveUrl, payload, message, function() {
        if (to === 'unused') {
          self.processMoveToUnusedFromPanel(adjudicator, fromDebate, dontPushToUnused)
        } else {
          var toDebateChair = self.getDebateChair(toDebate).id;
          if (from === 'unused') {
            self.processMoveToPanelFromUnused(adjudicator, toDebate, toPosition)
            // If being dropped into an occupied chair position move old chair to unused
            if (toPosition === 'C' && toDebateChair) {
              self.saveMove(toDebateChair, toDebate.id, 'unused')
            }
          } else {
            if (toPosition !== 'C' || !toDebateChair) {
              // If not being dropped into the chair position; or if the chair position is empty
              self.processMoveToPanelFromPanel(adjudicator, fromDebate, toDebate, toPosition)
            } else {
              // If being moved to a filled chair we always swap with the previous position
              console.log('chair to chair')
              // self.processMoveToCurrentlyFilledChair(adjudicator, fromDebate, toDebate, isSwap)
            }
          }
        }
      })
    },
    processMoveToUnusedFromPanel(adjudicator, fromDebate, dontPushToUnused) {
      // Moving to Unused from a debate panel
      fromDebate.panel = _.filter(fromDebate.panel, function(panellist) {
        return panellist.adjudicator !== adjudicator
      })
      if (!dontPushToUnused) {
        this.unallocatedItems.push(adjudicator) // Need to push; not append
      }
    },
    processMoveToPanelFromUnused(adjudicator, toDebate, toPosition) {
      // If moving from unused needed to remove the adjudicator from unallcoated items
      var index = this.unallocatedItems.indexOf(adjudicator)
      this.unallocatedItems.splice(index, 1)
      toDebate.panel.push({ 'adjudicator': adjudicator, 'position': toPosition })
    },
    processMoveToPanelFromPanel(adjudicator, fromDebate, toDebate, toPosition) {
      // And trigger a save to remove them from their old position
      this.saveMove(adjudicator.id, fromDebate.id, 'unused', 'U', true)
      // If moving from an existing debate panel add the adj
      toDebate.panel.push({ 'adjudicator': adjudicator, 'position': toPosition })
    },
    processMoveToCurrentlyFilledChair(adjudicator, fromDebate, toDebate, isSwap) {
      // If moving from one chair position to another chair position; swap them
      // The isSwap override is here to prevent never ending recursive recalls
      // If moving from an existing debate into a debate with a venue; do a swap
      if (!isSwap) {
        this.saveMove(toDebate.venue.id, toDebate.id, fromDebate.id, false, true)
      }
      toDebate.panel.push({ 'adjudicator': adjudicator, 'position': 'C' })
    },
  }
}
</script>