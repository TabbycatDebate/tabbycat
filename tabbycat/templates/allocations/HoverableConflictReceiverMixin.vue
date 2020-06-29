<script>
// This responds to the change in the VueX state and checks an individual item against them
// Inheritors must prove a clashableType and clashableID
import { mapGetters } from 'vuex'

export default {
  methods: {
    getConflictsForType: function (conflictType) {
      if (this.clashableType === 'team' && conflictType === 'clash') {
        return this.teamClashesForItem(this.clashableID)
      } else if (this.clashableType === 'team' && conflictType === 'history') {
        return this.teamHistoriesForItem(this.clashableID)
      } else if (this.clashableType === 'adjudicator' && conflictType === 'clash') {
        return this.adjudicatorClashesForItem(this.clashableID)
      } else if (this.clashableType === 'adjudicator' && conflictType === 'history') {
        return this.adjudicatorHistoriesForItem(this.clashableID)
      }
    },
  },
  computed: {
    hasHoverClashConflict: function () {
      // These are many to one; no need to lookup the target's conflicts as can be inferred via ID
      const sourceClashes = this.currentHoverClashes
      if (!sourceClashes) { return false }
      // Hovered over an adj; highlight a team
      if ('team' in sourceClashes && this.clashableType === 'team') {
        for (const sourceClash of sourceClashes.team) {
          if (sourceClash.id === this.clashableID) {
            return true
          }
        }
      }
      // Hovered over an adj or a team; highlight an adj
      if ('adjudicator' in sourceClashes && this.clashableType === 'adjudicator') {
        for (const sourceClash of sourceClashes.adjudicator) {
          if (sourceClash.id === this.clashableID) {
            return true
          }
        }
      }
      return false
    },
    hasHoverInstitutionalConflict: function () {
      const sourceClashes = this.currentHoverClashes
      if (!sourceClashes) { return false }
      const itemClashes = this.getConflictsForType('clash')
      if (!itemClashes) { return false }
      if ('institution' in sourceClashes && 'institution' in itemClashes) {
        for (const sourceClash of sourceClashes.institution) {
          for (const itemClash of itemClashes.institution) {
            if (sourceClash.id === itemClash.id) {
              return true
            }
          }
        }
      }
      return false
    },
    hasHoverHistoryConflict: function () {
      // These are many to one; no need to lookup the target's conflicts as can be inferred via ID
      if (!this.currentHoverHistories) {
        return false // This is called by template directly; hence the need to check for null
      }
      const sourceHistories = this.currentHoverHistories
      let smallestAgo = 99
      // Hovered over an adj; highlight a team
      if ('team' in sourceHistories && this.clashableType === 'team') {
        for (const sourceHistory of sourceHistories.team) {
          if (sourceHistory.id === this.clashableID) {
            if (sourceHistory.ago < smallestAgo) {
              smallestAgo = sourceHistory.ago // Want to ensure we show the most recent clash
            }
          }
        }
      }
      // Hovered over an adj or a team; highlight an adj
      if ('adjudicator' in sourceHistories && this.clashableType === 'adjudicator') {
        for (const sourceHistory of sourceHistories.adjudicator) {
          if (sourceHistory.id === this.clashableID) {
            if (sourceHistory.ago < smallestAgo) {
              smallestAgo = sourceHistory.ago // Want to ensure we show the most recent clash
            }
          }
        }
      }
      if (smallestAgo === 99) {
        return false
      } else {
        return smallestAgo
      }
    },
    hoverConflictsCSS: function () {
      if (this.currentHoverClashes === null && this.currentHoverHistories === null) {
        return ''
      } else if (this.hasHoverClashConflict) {
        return 'conflictable hover-adjudicator'
      } else if (this.hasHoverInstitutionalConflict) {
        return 'conflictable hover-institution'
      } else if (this.hasHoverHistoryConflict) {
        return `conflictable hover-histories-${this.hasHoverHistoryConflict}-ago`
      }
      return ''
    },
    ...mapGetters(['adjudicatorClashesForItem', 'teamClashesForItem',
      'adjudicatorHistoriesForItem', 'teamHistoriesForItem',
      'currentHoverClashes', 'currentHoverHistories']),
  },
}
</script>
