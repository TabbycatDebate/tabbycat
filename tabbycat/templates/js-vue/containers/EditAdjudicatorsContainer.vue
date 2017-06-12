<template>
  <div class="col-md-12 draw-container allocation-container">

    <allocation-actions :round-info="roundInfo"></allocation-actions>

    <div class="row">
      <div class="vertical-spacing" id="messages-container"></div>
    </div>

    <div class="vertical-spacing">
      <draw-header :positions="roundInfo.positions">
        <div class="thead flex-cell flex-4 text-center" data-toggle="tooltip" title="Set the debate's priority (higher importances will be allocated better panels)." slot="himportance">
          <span>Priority</span>
        </div>
        <template slot="hvenue"><!-- Hide Venues --></template>
        <template slot="hpanel">
          <div class="thead flex-cell flex-12 vue-droppable-container">
            <span>Chair</span>
          </div>
          <div class="thead flex-cell flex-12 vue-droppable-container">
            <span>Panel</span>
          </div>
          <div class="thead flex-cell flex-12 vue-droppable-container">
            <span>Trainees</span>
          </div>
        </template>
      </draw-header>
      <debate v-for="debate in debates" :debate="debate" :key="debate.id" :round-info="roundInfo">
        <div class="draw-cell flex-4" slot="simportance">
          <debate-importance :id="debate.id" :importance="debate.importance"></debate-importance>
        </div>
        <template slot="svenue"><!-- Hide Venues --></template>
        <template slot="spanel">
          <div class="draw-cell panel-container flex-36 flex-horizontal">
            <template v-for="position in adjPositions">
              <div :class="['vue-droppable-container', 'position-container-' + position]">
                <droppable-generic :assignment-id="debate.id"
                                   :assignment-position="position"
                                   :extra-css="'flex-horizontal'"
                                   :locked="debate.locked">
                  <draggable-adjudicator
                    v-for="da in getAdjudicatorsByPosition(debate, position)"
                    :adjudicator="da.adjudicator" :key="da.adjudicator.id"
                    :debate-id="debate.id" :locked="debate.locked">
                  </draggable-adjudicator>
                </droppable-generic>
              </div>
            </template>
          </div>
        </template>
      </debate>
    </div>

    <unallocated-items-container>
      <div v-for="unallocatedAdj in unallocatedAdjsByScore">
        <draggable-adjudicator :adjudicator="unallocatedAdj"
                               :locked="unallocatedAdj.locked"></draggable-adjudicator>
      </div>
    </unallocated-items-container>

    <slide-over-item :subject="slideOverItem"></slide-over-item>

  </div>
</template>

<script>
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import AdjudicatorMovingMixin from '../ajax/AdjudicatorMovingMixin.vue'
import HighlightableContainerMixin from '../allocations/HighlightableContainerMixin.vue'
import AllocationActions from '../allocations/AllocationActions.vue'
import DebateImportance from '../allocations/DebateImportance.vue'
import ConflictsCoordinatorMixin from '../allocations/ConflictsCoordinatorMixin.vue'
import DraggableAdjudicator from '../draganddrops/DraggableAdjudicator.vue'
import _ from 'lodash'

export default {
  mixins: [AdjudicatorMovingMixin, DrawContainerMixin,
           HighlightableContainerMixin, ConflictsCoordinatorMixin],
  components: { AllocationActions, DebateImportance, DraggableAdjudicator },
  created: function() {
    this.$eventHub.$on('update-importance', this.updateImportance)
  },
  computed: {
    unallocatedAdjsByScore: function() {
      return _.reverse(_.sortBy(this.unallocatedItems, ['score']))
    },
    allAdjudicatorsById: function() {
      return _.keyBy(this.adjudicators.concat(this.unallocatedItems), 'id')
    },
  },
  methods: {
    getAdjudicatorsByPosition: function(debate, position) {
      return _.filter(debate.panel, { 'position': position })
    },
    moveToDebate(payload, assignedId, assignedPosition) {
      if (payload.debate === assignedId) {
        // Check that it isn't an in-panel move
        var thisDebate = this.debatesById[payload.debate]
        var fromPanellist = _.find(thisDebate.panel, function(panellist) {
          return panellist.adjudicator.id === payload.adjudicator;
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
      this.ajaxSave(url, payload, message, function() {
        debate.importance = importance // Update model data
      })
    },
  }
}
</script>
