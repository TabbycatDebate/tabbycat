<script>
import MovingMixin from '../ajax/MovingMixin.vue'
import _ from 'lodash'

export default {
  mixins: [MovingMixin],
  methods: {
    getPanellist(debate, adjudicator=false, position=false) {
      var potentialPanellist = _.find(debate.panel, function(panellist) {
        if (adjudicator) { return panellist.adjudicator.id === adjudicator.id }
        if (position) { return panellist.position === position }
      })
      if (_.isUndefined(potentialPanellist)) { return false } else {
        return potentialPanellist
      }
    },
    removefromPanel(debate, adjudicator) {
      var adjIndex = _.findIndex(debate.panel, function(panellist) {
        return panellist.adjudicator.id == adjudicator.id;
      });
      debate.panel.splice(adjIndex, 1)
    },
    saveMoveForType(adjudicatorId, fromDebate, toDebate, toPosition=null) {
      var adjudicator = this.allAdjudicatorsById[adjudicatorId]
      var currentChair = this.getPanellist(toDebate, false, "C").adjudicator
      var oldPosition = this.getPanellist(fromDebate, adjudicator, false).position
      var addToUnused = []
      var removeFromUnused = []
      // Data Logic
      if (toDebate === 'unused') {
        // Moving to unsed from panel
        this.removefromPanel(fromDebate, adjudicator)
        addToUnused.push(adjudicator)
      } else if (fromDebate === 'unused') {
        // Moving from unsued to a panel
        toDebate.panel.push({ 'adjudicator': adjudicator, 'position': toPosition })
        removeFromUnused.push(adjudicator)
        // If being dropped into an occupied chair position move old chair to unused
        if (toPosition === 'C' && currentChair) {
          this.removefromPanel(toDebate, currentChair)
          addToUnused.push(currentChair)
        }
      } else if (toDebate !== 'unused' && fromDebate !== 'unused') {
        // If moving from panel to panel
        if (toPosition === 'C' && currentChair) {
          // Moving to a currently-occupied chair position from anywhere; ie a swap
          this.removefromPanel(toDebate, currentChair)
          this.removefromPanel(fromDebate, adjudicator)
          toDebate.panel.push({ 'adjudicator': adjudicator, 'position': toPosition })
          fromDebate.panel.push({ 'adjudicator': currentChair, 'position': oldPosition })
        } else {
          // Remove them from their current panel; add to new panel
          this.removefromPanel(fromDebate, adjudicator)
          toDebate.panel.push({ 'adjudicator': adjudicator, 'position': toPosition })
        }
      }
      // Saving
      var debatesToSave = this.determineDebatesToSave(fromDebate, toDebate)
      var message = ' move of adj ' + adjudicator.name + ' to ' + toPosition + ' '
      this.postModifiedDebates(debatesToSave, addToUnused, removeFromUnused,
                               message)
    }
  }
}
</script>
