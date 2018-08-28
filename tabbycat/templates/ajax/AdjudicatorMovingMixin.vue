<script>
import _ from 'lodash'
import MovingMixin from '../ajax/MovingMixin.vue'

export default {
  mixins: [MovingMixin],
  methods: {
    debateCheckIfShouldSave () {
      return true
    },
    getPanellist (debate, adjudicator = false, position = false) {
      const potentialPanellist = _.find(debate.debateAdjudicators, (panellist) => {
        if (adjudicator) {
          return panellist.adjudicator.id === adjudicator.id
        }
        return panellist.position === position
      })
      if (_.isUndefined(potentialPanellist)) { return false }
      return potentialPanellist
    },
    removefromPanel (debate, adjudicator) {
      const adjs = debate.debateAdjudicators
      const adjIndex = _.findIndex(adjs, panellist => panellist.adjudicator.id === adjudicator.id)
      debate.debateAdjudicators.splice(adjIndex, 1)
    },
    saveMoveForType (adjudicatorId, fromDebate, toDebate, toPosition = null) {
      const adjudicator = this.adjudicatorsById[adjudicatorId]
      const currentChair = this.getPanellist(toDebate, false, 'C').adjudicator
      const oldPosition = this.getPanellist(fromDebate, adjudicator, false).position
      const addToUnused = []
      const removeFromUnused = []

      // Data Logic
      if (toDebate === 'unused') {
        // Moving to unsed from panel
        this.removefromPanel(fromDebate, adjudicator)
        addToUnused.push(adjudicator)
      } else if (fromDebate === 'unused') {
        // Moving from unsued to a panel
        toDebate.debateAdjudicators.push({ adjudicator: adjudicator, position: toPosition })
        if (!this.roundInfo.adjudicatorDoubling) {
          // Only remove if the tournament has set double allocations
          removeFromUnused.push(adjudicator)
        }
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
          toDebate.debateAdjudicators.push({
            adjudicator: adjudicator, position: toPosition,
          })
          fromDebate.debateAdjudicators.push({
            adjudicator: currentChair, position: oldPosition,
          })
        } else {
          // Remove them from their current panel; add to new panel
          this.removefromPanel(fromDebate, adjudicator)
          toDebate.debateAdjudicators.push({
            adjudicator: adjudicator, position: toPosition,
          })
        }
      }
      // After saving the
      const movedPanellists = _.concat(toDebate.debateAdjudicators, fromDebate.debateAdjudicators)
      const movedAdjudicators = _.mapValues(movedPanellists, 'adjudicator')
      const movedAdjsById = _.keyBy(movedAdjudicators, 'id')

      // Saving
      const debatesToSave = this.determineDebatesToSave(fromDebate, toDebate)
      const message = `move of adj ${adjudicator.name} to ${toPosition} `
      this.postModifiedDebates(
        debatesToSave, addToUnused, removeFromUnused,
        movedAdjsById, message
      )
    },
  },
}
</script>
