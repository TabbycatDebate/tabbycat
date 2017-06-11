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
      // console.log('Removing ' + adjudicator.name + ' from ' + this.niceNameForDebate(debate.id))
      var adjIndex = _.findIndex(debate.panel, function(panellist) {
        return panellist.adjudicator == adjudicator;
      });
      debate.panel.splice(adjIndex, 1)
    },
    saveMoveForType(adjudicatorId, fromDebate, toDebate, toPosition=null) {
      var adjudicator = this.allAdjudicatorsById[adjudicatorId]
      var currentChair = this.getPanellist(toDebate, false, "C").adjudicator
      var addToUnused = []
      var removeFromUnused = []
      // Data Logic
      if (toDebate === 'unused') {
        this.removefromPanel(fromDebate, adjudicator)
        addToUnused.push(adjudicator)
      }
      if (fromDebate === 'unused') {
        removeFromUnused.push(adjudicator)
        toDebate.panel.push({ 'adjudicator': adjudicator, 'position': toPosition })
        // If being dropped into an occupied chair position move old chair to unused
        if (toPosition === 'C' && currentChair) {
          this.removefromPanel(toDebate, currentChair)
          addToUnused.push(currentChair)
        }
      }
      if (toDebate !== 'unused' && fromDebate !== 'unused') {
        var oldPosition = this.getPanellist(fromDebate, adjudicator, false).position
        // Moving to a panel from a panel
        if (toPosition === 'C' && currentChair) {
          // Moving to a currently-occupied chair position from anywhere
          this.removefromPanel(toDebate, currentChair)
          fromDebate.panel.push({ 'adjudicator': currentChair, 'position': oldPosition })
        }
        this.removefromPanel(fromDebate, adjudicator)
        toDebate.panel.push({ 'adjudicator': adjudicator, 'position': toPosition })
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