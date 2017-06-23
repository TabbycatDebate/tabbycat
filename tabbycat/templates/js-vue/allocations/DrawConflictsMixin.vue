<script>
import ConflictsCoordinatorMixin from '../allocations/ConflictsCoordinatorMixin.vue'
import _ from 'lodash'

export default {
  // Designed to be applied to manage conflicts across all of the tournament on hover
  mixins: [ConflictsCoordinatorMixin],
  computed: {
    filteredClashes: function() {
      return this.conflicts // Dummy method as overriden by DebateConflictsMixin
    },
    filteredHistories: function() {
      return this.histories // Dummy method as overriden by DebateConflictsMixin
    }
  },
  methods: {
    getDebateConflictables(debate, type) {
      // Creates a per-debate subset of conflicts/histories for DebateConflictsMixin
      // to determine in-panel conflicts using ConflictsCoordinator
      var panellistIds = _.map(debate.panel, function(panellist) {
        return panellist.adjudicator.id
      })
      return _.pick(this[type], panellistIds)
    },
  },
}
</script>
