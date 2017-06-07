<template>
  <div class="col-md-12 draw-container allocation-container">

    <allocation-actions-container
      :round-info="roundInfo" :back-url="backUrl"></allocation-actions-container>

    <div class="vertical-spacing" id="messages-container"></div>

    <slide-over-item :subject="slideOverItem"></slide-over-item>

    <draw-header :positions="positions">
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

    <debate v-for="debate in debates" :debate="debate" :key="debate.id">
      <div class="draw-cell flex-4" slot="simportance">
        <debate-importance :id="debate.id" :importance="debate.importance"></debate-importance>
      </div>
      <template slot="svenue"><!-- Hide Venues --></template>
      <template slot="spanel">
        <div class="draw-cell flex-12 vue-droppable-container">
          <droppable-generic>
            <draggable-adjudicator v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'C')"
              :adjudicator="debateAdjudicator.adjudicator"
              :key="debateAdjudicator.adjudicator.id"></draggable-adjudicator>
          </droppable-generic>
        </div>
        <div class="draw-cell flex-12 vue-droppable-container">
          <droppable-generic>
            <draggable-adjudicator v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'P')"
              :adjudicator="debateAdjudicator.adjudicator"
              :key="debateAdjudicator.adjudicator.id"></draggable-adjudicator>
          </droppable-generic>
        </div>
        <div class="draw-cell flex-12 vue-droppable-container">
          <droppable-generic>
            <draggable-adjudicator v-for="debateAdjudicator in getAdjudicatorsByPosition(debate, 'T')"
              :adjudicator="debateAdjudicator.adjudicator"
              :key="debateAdjudicator.adjudicator.id"></draggable-adjudicator>
          </droppable-generic>
        </div>
      </template>
    </debate>

    <unallocated-items-container>
      <div v-for="unallocatedAdj in unallocatedAdjsByScore">
        <draggable-adjudicator :adjudicator="unallocatedAdj"></draggable-adjudicator>
      </div>
    </unallocated-items-container>

  </div>
</template>

<script>
import AllocationActionsContainer from '../allocations/AllocationActions.vue'
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import UnallocatedItemsContainer from '../containers/UnallocatedItemsContainer.vue'
import DrawHeader from '../draw/DrawHeader.vue'
import Debate from '../draw/Debate.vue'
import DebateImportance from '../draw/DebateImportance.vue'
import AjaxMixin from '../draganddrops/DroppableGeneric.vue'
import DroppableGeneric from '../draganddrops/DroppableGeneric.vue'
import DraggableAdjudicator from '../draganddrops/DraggableAdjudicator.vue'
import SlideOverItem from '../infoovers/SlideOverItem.vue'
import _ from 'lodash'

export default {
  mixins: [DrawContainerMixin, AjaxMixin],
  components: {
    AllocationActionsContainer, UnallocatedItemsContainer, DrawHeader, Debate,
    DebateImportance, DroppableGeneric, DraggableAdjudicator, SlideOverItem
  },
  props: { roundInfo: Object },
  created: function() {
    this.$eventHub.$on('update-allocation', this.updateAllocation)
    this.$eventHub.$on('update-unallocated', this.updateUnallocated)
    this.$eventHub.$on('update-importance', this.updateImportance)
    this.$eventHub.$on('set-highlights', this.setHighlights)
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
    updateImportance: function(debateID, importance) {
      // This fires after autoAllocation; unclear why
      var debate = _.find(this.debates, { 'id': debateID })
      if (!_.isUndefined(debate)) {
        var url = this.roundInfo.updateImportanceURL
        var payload = { debate_id: debateID, importance: importance }
        var message = 'debate ' + debate.id + '\'s importance'
        this.ajaxSave(url, payload, message, function() {
          debate.importance = importance // Update model data
          console.log('Updated data: importance for ' + debate.id + ' to ' + importance)
        })
      } else {
        this.ajaxError(resourceType, "", "Couldnt find debate to update")
      }
    },
    updateAllocation: function(updatedDebates) {
      this.debates = updatedDebates
    },
    updateUnallocated(updatedUnallocatedAdjudicators) {
      this.unallocatedItems = updatedUnallocatedAdjudicators
    },
    setHighlights(highlights) {
      _.forEach(this.teams, function(item) {
        item.highlights = highlights
      })
      _.forEach(this.adjudicators, function(item) {
        item.highlights = highlights
      })
      _.forEach(this.unallocatedItems, function(item) {
        item.highlights = highlights
      })
    }
  }
}
</script>
