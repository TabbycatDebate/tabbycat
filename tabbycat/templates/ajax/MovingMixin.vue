<script>
import _ from 'lodash'
import AjaxMixin from '../ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  methods: {
    niceNameForDebate: function (debateId) {
      if (debateId === 'unused') {
        return 'unused'
      }
      const debate = this.debatesById[debateId]
      // Used for debugging
      let niceName = `debate ${debate.id} (`
      _.forEach(debate.debateTeams, (dt) => {
        if (dt.team !== null) {
          niceName += `${dt.team.short_name}, `
        }
      })
      niceName = niceName.substring(0, niceName.length - 2)
      niceName += ')'
      return niceName
    },
    saveMove (movedItemId, fromDebateId, toDebateId, toPosition = null) {
      let fromDebate = this.debatesById[fromDebateId]
      if (_.isUndefined(fromDebate)) { // Undefined if coming from unused
        fromDebate = 'unused'
      }
      let toDebate = this.debatesById[toDebateId]
      if (_.isUndefined(toDebate)) { // Undefined if going to unused
        toDebate = 'unused'
      }

      // We clone each object so we can roll back to the originals if it fails
      const clonedToDebate = _.cloneDeep(toDebate)

      // For in-panel swaps we want them referring to the same variable
      const fromSameDebate = (toDebate.id === fromDebate.id)
      const clonedFromDebate = fromSameDebate ? clonedToDebate : _.cloneDeep(fromDebate)

      this.saveMoveForType(movedItemId, clonedFromDebate, clonedToDebate, toPosition)
    },
    determineDebatesToSave (fromDebate, toDebate) {
      // Note children must implement a debateCheckIfShouldSave()
      const debatesToSave = []
      if (fromDebate.id === toDebate.id && this.debateCheckIfShouldSave(toDebate)) {
        return [toDebate]
      }
      if (toDebate !== 'unused' && this.debateCheckIfShouldSave(toDebate)) {
        debatesToSave.push(toDebate)
      }
      if (fromDebate !== 'unused' && this.debateCheckIfShouldSave(fromDebate)) {
        debatesToSave.push(fromDebate)
      }
      return debatesToSave
    },
    setLocked (item, itemDictionary, lockStatus) {
      const possibleItemsToLock = itemDictionary
      // When locking we need to lock the original debate; not the cloned
      if (_.isUndefined(possibleItemsToLock[item.id])) {
        this.showErrorAlert(
          ' a debate',
          'the debate doesn\'t seem to exist in the database anymore (e.g. the draw was remade)'
        )
      } else {
        possibleItemsToLock[item.id].locked = lockStatus
      }
    },
    postModifiedDebates (
      debatesToSave, addToUnused, removeFromUnused,
      reallocateToPanel, messageStart
    ) {
      const self = this
      // Lock the debate and unused items to prevent edits
      _.forEach(debatesToSave, (debateToSave) => {
        self.setLocked(debateToSave, self.debatesById, true)
      })
      _.forEach(removeFromUnused, (itemToUse) => {
        self.setLocked(itemToUse, self.unallocatedById, true)
      })
      // Issue an AJAX request for each debate
      _.forEach(debatesToSave, (debateToSave) => {
        const message = messageStart + self.niceNameForDebate(debateToSave.id)
        self.ajaxSave(
          self.roundInfo.saveUrl, debateToSave, message,
          self.processSaveSuccess, self.processSaveFailure,
          {
            addToUnused: addToUnused,
            removeFromUnused: removeFromUnused,
            reallocateToPanel: reallocateToPanel,
          }
        )
      })
    },
    processSaveSuccess: function (dataResponse, savedDebate, returnPayload) {
      // Replace old debate object with new one
      const oldDebateIndex = _.findIndex(this.debates, { id: savedDebate.id })
      if (oldDebateIndex !== -1) {
        const self = this
        const newDebate = dataResponse
        // For the teams and adjudidcators teams in the new debate object
        // we need to swap them out for the representations of them that were
        // stored before they were sent over; as they come back without the
        // initial annotations and thus don't have conflicts, regions, etc

        // Only swap out on the edit adjs page
        if (returnPayload.reallocateToPanel) {
          // Break categories aren't supplied by the server; set from old debate
          newDebate.liveness = savedDebate.liveness

          // For teams they dont change so we can use the global variable
          newDebate.debateTeams = _.map(newDebate.debateTeams, (dt) => {
            if (dt.team !== null) {
              const id = dt.team.id
              if (_.has(self.teamsById, id)) {
                dt.team = self.teamsById[id]
              } else {
                console.error('ERROR: Couldnt find team ', dt.team.short_name)
              }
            }
            return dt
          })

          // For adjudicators we saved/stored a list of all adjs when saving and need to restore
          const originalAdjsById = returnPayload.reallocateToPanel
          newDebate.debateAdjudicators = _.map(newDebate.debateAdjudicators, (da) => {
            const id = da.adjudicator.id
            if (_.has(originalAdjsById, id)) {
              da.adjudicator = originalAdjsById[id]
            } else {
              console.error('ERROR: Couldnt find adj ', da.adjudicator.name)
            }
            return da
          })
        }

        // Remove/replace old debate with new Debate object
        this.debates.splice(oldDebateIndex, 1, newDebate)
        console.debug(`    VUE: Loaded new debate for ${this.niceNameForDebate(newDebate.id)}`)
      } else {
        console.warn("    VUE: Shouldn't happen; couldnt find old debates position")
      }
      // Remove/add relevant items to unused area
      _.forEach(returnPayload.addToUnused, (unusedItem) => {
        self.unallocatedItems.push(unusedItem)
        unusedItem.locked = false
      })
      _.forEach(returnPayload.removeFromUnused, (usedItem) => {
        self.unallocatedItems.splice(self.unallocatedItems.indexOf(usedItem), 1)
      })
    },
    processSaveFailure: function (unsavedDebate, returnPayload) {
      this.setLocked(unsavedDebate, this.debatesById, false)
      const self = this
      _.forEach(returnPayload.removeFromUnused, (itemToUse) => {
        self.setLocked(itemToUse, self.unallocatedById, false)
      })
    },
  },
}
</script>
