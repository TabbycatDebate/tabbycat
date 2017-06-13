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
    getConflicts(conflictingItem, conflictingItemType) {
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
      var histories = false
      if (conflictingItemType === 'adjudicator') {
        histories = this.histories[conflictingItem.id]
      }
      // } else if (conflictingItemType === 'team') {
      //   var reversedHistories = _.filter(this.histories, function(h) {
      //     return h[self.conflictableType] === conflictingItem.id
      //   })
      // }
      if (!_.isUndefined(histories)) {
        return histories
      } else {
        return false
      }
    },
    setConflicts: function(conflictingItem, conflictingItemType) {
      console.log('Setting conflicts for ', conflictingItemType, conflictingItem.id)
      var conflicts = this.getConflicts(conflictingItem, conflictingItemType)
      var histories = this.getHistories(conflictingItem, conflictingItemType)
      this.$eventHub.$emit('set-conflicts-for', conflictingItem,
                           conflicts, histories, true)
    },
    unsetConflicts: function(conflictingItem, conflictingItemType) {
      console.log('Setting conflicts for ', conflictingItemType, conflictingItem.id)
      var conflicts = this.getConflicts(conflictingItem, conflictingItemType)
      var histories = this.getHistories(conflictingItem, conflictingItemType)
      this.$eventHub.$emit('set-conflicts-for', conflictingItem,
                           conflicts, histories, false)
    }
  }
}
</script>
