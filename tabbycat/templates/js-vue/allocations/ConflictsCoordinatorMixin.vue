<script>
import _ from 'lodash'

export default {
  // An item that contains a list of conflicts and histories; and manages
  // the task of figuring out which things conflict with the nominated
  // conflictable item according to those conflicts/histories

  props: ['conflicts', 'histories'],
  methods: {
    setOrUnsetConflicts: function(conflictingItem, conflictingItemType,
                                  hoverOrPanel, conflictState) {
      // Load up the conflicting items clash lists/histories
      // Not in the case of debates this will limit just to the team/adj
      // if (conflictState && conflictingItem.id === 96) { console.log('Checking for Bennie') }
      if (conflictingItemType === 'adjudicator') {
        var clashes = this.filteredClashes[conflictingItem.id]
        var seens = this.filteredHistories[conflictingItem.id]
        // if (conflictState && conflictingItem.id === 96) { console.log('  Bennie clashes', clashes) }
        // if (conflictState && conflictingItem.id === 96) { console.log('  Bennie seens', seens) }
      } else if (conflictingItemType === 'team') {
        var clashes = this.getTeamClashes(conflictingItem)
        var seens = this.getTeamSeens(conflictingItem)
      }
      var self = this
      // For each of these clashes/histories emit events to turn them on
      _.forEach(clashes, function(clashList, clashType) {
        _.forEach(clashList, function(clashedId) {
          var eventCode = 'set-clashes-for-' + clashType + '-' + clashedId
          // console.log(eventCode)
          self.$eventHub.$emit(eventCode, hoverOrPanel, conflictState, clashType)
        })
      })
      _.forEach(seens, function(seenList, seenType) {
        _.forEach(seenList, function(seenItem) {
          var eventCode = 'set-seens-for-' + seenType + '-' + seenItem.id
          // console.log(eventCode)
          var seenState = conflictState === false ? false : seenItem.ago
          self.$eventHub.$emit(eventCode, hoverOrPanel, seenState, seenType)
        })
      })
    },
    getTeamClashes(conflictingItem) {
      // Because conflicts are organised by adj-id as key we need to search
      // through them & identify those applicable from the team's perspective
      var reversedConflicts = {'adjudicator': [], 'institution': [] }
      _.forEach(this.conflicts, function(adjConflicts, adjId) {
        var teamsInstitutionId = conflictingItem.institution.id
        if (_.includes(adjConflicts['institution'], teamsInstitutionId)) {
          reversedConflicts.institution.push(teamsInstitutionId)
        }
        var teamsId = conflictingItem.id
        if (_.includes(adjConflicts['team'], teamsId)) {
          reversedConflicts.adjudicator.push(parseInt(adjId)) // Keys=strings
        }
      });
      return reversedConflicts
    },
    getTeamSeens(conflictingItem) {
      var reversedHistories = {'adjudicator': []}
      _.forEach(this.histories, function(adjHistories, adjId) {
        _.forEach(adjHistories['team'], function(ah) {
          if (ah.id === conflictingItem.id) {
            reversedHistories['adjudicator'].push({
              'ago': ah.ago, 'id': parseInt(adjId)})
          }
        })
      })
      return reversedHistories
    },
  }
}
</script>
