<script>
import _ from 'lodash'

export default {
  props: ['conflicts', 'histories'],
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('show-conflicts-for', this.setConflicts)
    this.$eventHub.$on('hide-conflicts-for', this.unsetConflicts)
  },
  computed: {

  },
  methods: {
    getClashes(conflictingItem, conflictingItemType) {
      if (conflictingItemType === 'adjudicator') {
        return this.conflicts[conflictingItem.id]
      } else if (conflictingItemType === 'team') {
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
      }
    },
    getHistories(conflictingItem, conflictingItemType) {
      if (conflictingItemType === 'adjudicator') {
        return this.histories[conflictingItem.id]
      } else if (conflictingItemType === 'team') {
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
      }
    },
    setConflicts: function(conflictingItem, conflictingItemType) {
      console.log('Setting conflicts for ', conflictingItemType, conflictingItem.id)
      var conflicts = this.getClashes(conflictingItem, conflictingItemType)
      var histories = this.getHistories(conflictingItem, conflictingItemType)
      this.$eventHub.$emit('set-conflicts-for', conflictingItem,
                           conflicts, histories, true)
    },
    unsetConflicts: function(conflictingItem, conflictingItemType) {
      console.log('Setting conflicts for ', conflictingItemType, conflictingItem.id)
      var conflicts = this.getClashes(conflictingItem, conflictingItemType)
      var histories = this.getHistories(conflictingItem, conflictingItemType)
      this.$eventHub.$emit('set-conflicts-for', conflictingItem,
                           conflicts, histories, false)
    }
  }
}
</script>
