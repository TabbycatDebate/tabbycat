<template>
  <div class="draw-container allocation-container">

    <allocation-actions :round-info="roundInfo" :sharding="sharding.enabled"
                        :percentiles="percentileThresholds"></allocation-actions>

    <div class="row">
      <div class="mt-3 col allocation-messages" id="messages-container"></div>
    </div>

    <div class="mb-3">
      <draw-header :round-info="roundInfo" @resort="updateSorting"
                   :sort-key="sortKey" :sort-order="sortOrder">

        <div slot="himportance" class="thead flex-cell flex-6 vue-sortable"
             @click="updateSorting('importance')" data-toggle="tooltip"
             title="The debate's priority. Higher priorities will be allocated
              better adjudicators during auto-allocation." >
          <div class="d-flex align-items-end">
            <span class="tooltip-trigger">Priority</span>
            <div :class="sortClasses('importance')">
              <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
            </div>
          </div>
        </div>

        <template slot="hvenue">
          <span></span> <!-- Hide Venues -->
        </template>


        <template slot="hpanel">
          <div :class="['thead flex-cell text-center',
                        'flex-' + (adjPositions.length > 2 ? 10 : adjPositions.length > 1 ? 8 : 12)]">
            <div class="d-flex align-items-end">
              <span>Chair</span>
            </div>
          </div>
          <div v-if="adjPositions.indexOf('P') !== -1"
               :class="['thead flex-cell text-center',
                        'flex-' + (adjPositions.length > 2 ? 17: 16)]">
            <div class="d-flex align-items-end">
              <span>Panel</span>
            </div>
          </div>
          <div v-if="adjPositions.indexOf('T') !== -1"
               :class="['thead flex-cell text-center',
                        'flex-' + (adjPositions.length > 2 ? 10: 16)]">
            <div class="d-flex align-items-end">
              <span>Trainees</span>
            </div>
          </div>
        </template>

      </draw-header>

      <debate v-for="debate in dataOrderedByKey"
              :debate="debate" :key="debate.id" :round-info="roundInfo">

        <div class="draw-cell flex-6" slot="simportance">
          <debate-importance :id="debate.id" :importance="debate.importance"></debate-importance>
        </div>

        <template slot="svenue">
          <span></span> <!-- Hide Venues -->
        </template>

        <template slot="spanel">
          <debate-panel :panel-adjudicators="debate.debateAdjudicators" :debate-id="debate.id"
                        :panel-teams="debate.debateTeams"
                        :percentiles="percentileThresholds"
                        :locked="debate.locked"
                        :round-info="roundInfo"
                        :adj-positions="adjPositions"></debate-panel>
        </template>

      </debate>
    </div>

    <unallocated-items-container v-if="!sharding.enabled">
      <div v-for="unallocatedAdj in unallocatedAdjsByOrder">
        <draggable-adjudicator :adjudicator="unallocatedAdj"
                               :percentiles="percentileThresholds"
                               :locked="unallocatedAdj.locked"></draggable-adjudicator>
      </div>
    </unallocated-items-container>

    <slide-over :subject="slideOverSubject"></slide-over>
    <allocation-intro-modal :show-intro-modal="showIntroModal"
                            :round-info="roundInfo"></allocation-intro-modal>

  </div>
</template>

<script>
import _ from 'lodash'
import percentile from 'stats-percentile'

import DrawContainerMixin from '../../draw/templates/DrawContainerMixin.vue'
import AdjudicatorMovingMixin from '../../templates/ajax/AdjudicatorMovingMixin.vue'
import AutoImportanceLogicMixin from '../../templates/allocations/AutoImportanceLogicMixin.vue'
import HighlightableContainerMixin from '../../templates/allocations/HighlightableContainerMixin.vue'
import AllocationActions from '../../templates/allocations/AllocationActions.vue'
import AllocationIntroModal from '../../templates/allocations/AllocationIntroModal.vue'
import DebateImportance from '../../templates/allocations/DebateImportance.vue'
import DebatePanel from '../../templates/allocations/DebatePanel.vue'
import DraggableAdjudicator from '../../templates/draganddrops/DraggableAdjudicator.vue'
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'


export default {
  mixins: [AjaxMixin, AdjudicatorMovingMixin, DrawContainerMixin,
           AutoImportanceLogicMixin, HighlightableContainerMixin],
  components: { AllocationActions, AllocationIntroModal, DebateImportance,
                DebatePanel, DraggableAdjudicator },
  props: { showIntroModal: Boolean },
  created: function () {
    // Watch for global conflict highlights
    this.$eventHub.$on('show-conflicts-for', this.setOrUnsetConflicts)
  },
  computed: {
    unallocatedAdjsByOrder: function () {
      if (this.roundInfo.roundIsPrelim === true) {
        return _.reverse(_.sortBy(this.unallocatedItems, ['score']))
      } else {
        return _.sortBy(this.unallocatedItems, ['name'])
      }
    },
    adjudicatorsById: function () {
      // Override DrawContainer() method to include unallocated
      return _.keyBy(this.adjudicators.concat(this.unallocatedItems), 'id')
    },
    percentileThresholds: function () {
      // For determining feedback rankings
      var allScores = _.map(this.adjudicatorsById, function (adj) {
        return parseFloat(adj.score)
      }).sort()
      var thresholds = []
      var letterGrades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C"]
      for (var i = 90; i > 10; i -= 10) {
        thresholds.push({
          'grade': letterGrades[0], 'cutoff': percentile(allScores, i), 'percentile': i
        })
        letterGrades.shift()
      }
      thresholds.push({'grade': "F", 'cutoff': 0, 'percentile': 10})
      return thresholds
    },
    adjPositions: function () {
      return this.roundInfo.adjudicatorPositions // Convenience
    },
  },
  methods: {
    moveToDebate(payload, assignedId, assignedPosition) {
      if (payload.debate === assignedId) {
        // Check that it isn't an in-panel move
        var thisDebate = this.debatesById[payload.debate]
        var fromPanellist = _.find(thisDebate.debateAdjudicators, function (da) {
          return da.adjudicator.id === payload.adjudicator;
        })
        if (assignedPosition === fromPanellist.position) {
          return // Moving to same debate/position; do nothing
        }
      }
      this.saveMove(payload.adjudicator, payload.debate, assignedId, assignedPosition)
    },
    moveToUnused(payload) {
      if (_.isUndefined(payload.debate)) {
        return // Moving to unused from unused; do nothing
      }
      this.saveMove(payload.adjudicator, payload.debate)
    },
  }
}
</script>
