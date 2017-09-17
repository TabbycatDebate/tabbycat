<template>
  <div class="draw-container allocation-container">

    <allocation-actions :round-info="roundInfo"
                        :percentiles="percentileThresholds"></allocation-actions>

    <div class="row">
      <div class="mb-3 col allocation-messages" id="messages-container"></div>
    </div>

    <div class="mb-3">
      <draw-header :positions="positions" @resort="updateSorting"
                   :sort-key="sortKey" :sort-order="sortOrder"
                   :round-info="roundInfo">

        <div class="thead flex-cell flex-5 vue-sortable" @click="updateSorting('importance')"
             data-toggle="tooltip" title="Set the debate's priority (higher importances will be allocated better panels)." slot="himportance">
          <span>Priority</span>
          <span :class="sortClasses('importance')"></span>
        </div>
        <template slot="hvenue"><!-- Hide Venues --></template>
        <template slot="hpanel">
          <div :class="['thead flex-cell text-center vue-droppable-container',
                        'flex-' + (adjPositions.length > 2 ? 10 : adjPositions.length > 1 ? 8 : 12)]">
            <span>Chair</span>
          </div>
          <div v-if="adjPositions.indexOf('P') !== -1"
               :class="['thead flex-cell text-center vue-droppable-container',
                        'flex-' + (adjPositions.length > 2 ? 17: 16)]">
            <span>Panel</span>
          </div>
          <div v-if="adjPositions.indexOf('T') !== -1"
               :class="['thead flex-cell text-center vue-droppable-container',
                        'flex-' + (adjPositions.length > 2 ? 10: 16)]">
            <span>Trainees</span>
          </div>
        </template>

      </draw-header>
      <debate v-for="debate in dataOrderedByKey"
              :debate="debate" :key="debate.id" :round-info="roundInfo">

        <div class="draw-cell flex-5" slot="simportance">
          <debate-importance :id="debate.id" :importance="debate.importance"></debate-importance>
        </div>
        <template slot="svenue"><!-- Hide Venues --></template>
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

    <unallocated-items-container>
      <div v-for="unallocatedAdj in unallocatedAdjsByOrder">
        <draggable-adjudicator :adjudicator="unallocatedAdj"
                               :percentiles="percentileThresholds"
                               :locked="unallocatedAdj.locked"></draggable-adjudicator>
      </div>
    </unallocated-items-container>

    <slide-over :subject="slideOverSubject"></slide-over>

  </div>
</template>

<script>
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import AdjudicatorMovingMixin from '../ajax/AdjudicatorMovingMixin.vue'
import HighlightableContainerMixin from '../allocations/HighlightableContainerMixin.vue'
import AllocationActions from '../allocations/AllocationActions.vue'
import DebateImportance from '../allocations/DebateImportance.vue'
import DebatePanel from '../allocations/DebatePanel.vue'
import DraggableAdjudicator from '../draganddrops/DraggableAdjudicator.vue'
import AjaxMixin from '../ajax/AjaxMixin.vue'

import percentile from 'stats-percentile'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin, AdjudicatorMovingMixin, DrawContainerMixin,
           HighlightableContainerMixin],
  components: { AllocationActions, DebateImportance, DebatePanel, DraggableAdjudicator },
  created: function() {
    this.$eventHub.$on('update-importance', this.updateImportance)
    // Watch for global conflict highlights
    this.$eventHub.$on('show-conflicts-for', this.setOrUnsetConflicts)
  },
  computed: {
    unallocatedAdjsByOrder: function() {
      if (this.roundInfo.roundIsPrelim === true) {
        return _.reverse(_.sortBy(this.unallocatedItems, ['score']))
      } else {
        return _.sortBy(this.unallocatedItems, ['name'])
      }
    },
    adjudicatorsById: function() {
      // Override DrawContainer() method to include unallocated
      return _.keyBy(this.adjudicators.concat(this.unallocatedItems), 'id')
    },
    percentileThresholds: function() {
      // For determining feedback rankings
      var allScores = _.map(this.adjudicatorsById, function(adj) {
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
    adjPositions: function() {
      return this.roundInfo.adjudicatorPositions // Convenience
    },
  },
  methods: {
    moveToDebate(payload, assignedId, assignedPosition) {
      if (payload.debate === assignedId) {
        // Check that it isn't an in-panel move
        var thisDebate = this.debatesById[payload.debate]
        var fromPanellist = _.find(thisDebate.debateAdjudicators, function(da) {
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
    updateImportance: function(debateID, importance) {
      var debate = _.find(this.debates, { 'id': debateID })
      if (_.isUndefined(debate)) {
        this.ajaxError("Debate\'s importance", "", "Couldnt find debate to update")
      }
      var url = this.roundInfo.updateImportanceURL
      var message = 'debate ' + debate.id + '\'s importance'
      var payload = { debate_id: debate.id, importance: importance }
      this.ajaxSave(url, payload, message, this.processImportanceSaveSuccess, null, null)
    },
    processImportanceSaveSuccess: function(dataResponse, payload, returnPayload) {
      var debateIndex = _.findIndex(this.debates, { 'id': payload.debate_id})
      if (debateIndex !== -1) {
        this.debates[debateIndex].importance = payload.importance
      }
    }
  }
}
</script>
