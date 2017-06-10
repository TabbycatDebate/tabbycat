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
          <div class="draw-cell flex-12 vue-droppable-container">
            <droppable-generic :assignment-id="debate.id" assignment-position="C">
              <draggable-adjudicator v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'C')"
                :adjudicator="debateAdjudicator.adjudicator"
                :key="debateAdjudicator.adjudicator.id"
                :debate-id="debate.id"></draggable-adjudicator>
            </droppable-generic>
          </div>
          <div class="draw-cell flex-12 vue-droppable-container">
            <droppable-generic :assignment-id="debate.id" assignment-position="P">
              <draggable-adjudicator v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'P')"
                :adjudicator="debateAdjudicator.adjudicator"
                :key="debateAdjudicator.adjudicator.id"
                :debate-id="debate.id"></draggable-adjudicator>
            </droppable-generic>
          </div>
          <div class="draw-cell flex-12 vue-droppable-container">
            <droppable-generic :assignment-id="debate.id" assignment-position="T">
              <draggable-adjudicator v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'T')"
                :adjudicator="debateAdjudicator.adjudicator"
                :key="debateAdjudicator.adjudicator.id"
                :debate-id="debate.id"></draggable-adjudicator>
            </droppable-generic>
          </div>
        </template>
      </debate>
    </div>

    <unallocated-items-container>
      <div v-for="unallocatedAdj in unallocatedAdjsByScore">
        <draggable-adjudicator :adjudicator="unallocatedAdj"></draggable-adjudicator>
      </div>
    </unallocated-items-container>

    <slide-over-item :subject="slideOverItem"></slide-over-item>

  </div>
</template>

<script>
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import HighlightableContainerMixin from '../allocations/HighlightableContainerMixin.vue'
import AllocationActions from '../allocations/AllocationActions.vue'
import DebateImportance from '../allocations/DebateImportance.vue'
import DraggableAdjudicator from '../draganddrops/DraggableAdjudicator.vue'
import _ from 'lodash'

export default {
  mixins: [DrawContainerMixin, HighlightableContainerMixin],
  components: { AllocationActions, DebateImportance, DraggableAdjudicator },
  props: { roundInfo: Object },
  created: function() {
    this.$eventHub.$on('update-importance', this.updateImportance)
  },
  computed: {
    unallocatedAdjsByScore: function() {
      return _.reverse(_.sortBy(this.unallocatedItems, ['score']))
    }
  },
  methods: {
    getAdjudicatorsByPosition: function(debate, position) {
      return _.filter(debate.panel, { 'position': position })
    },
    moveToUnused(payload) {
      if (_.isUndefined(payload.debate)) {
        return // Moving to unused from unused; do nothing
      }
      var adjudicator = this.adjudicatorsById[payload.adjudicator]
      var debate = this.debatesById[payload.debate]
      var message = 'moved adjudicator ' + adjudicator.name + ' to unused'
      var payload = { moved_item: adjudicator.id, debate_from: debate.id, debate_to: 'unused' }
      var self = this
      this.ajaxSave(this.roundInfo.saveUrl, payload, message, function() {
        var panel = self.debatesById[debate.id].panel // Convenience var
        // Make changes to the reactive property
        self.debatesById[debate.id].panel = _.filter(panel, function(da) {
          return da.adjudicator !== adjudicator
        })
        self.unallocatedItems.push(adjudicator) // Need to push; not append
      })
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
