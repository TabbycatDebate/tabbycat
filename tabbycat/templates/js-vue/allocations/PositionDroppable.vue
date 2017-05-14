<template>

  <div
    v-on:dragover.prevent
    v-on:dragenter="dragEnter"
    v-on:dragleave="dragLeave"
    v-on:drop="drop"
    v-on:set-dragged-adj="propogateSetAdj"
    v-on:unset-dragged-adj="propogateUnsetAdj"
    v-bind:class="['vue-droppable', {
        'panel-incomplete': isIncomplete,
        'vue-is-drag-enter': isDroppable,
        'flex-1': position !== 'P',
        'flex-2': position === 'P'
    }]"
    class="">

    <debate-adjudicator
      v-for="adj in adjudicatorsOrderedByScore"
      :adjorteam="adj"
      :position="position"
      :debate-id="debateId">
    </debate-adjudicator>

  </div>

</template>

<script>
import DebateAdjudicator from './DebateAdjudicator.vue'
import DroppableMixin from '../mixins/DroppableMixin.vue'
import _ from 'lodash'

export default {
  mixins: [DroppableMixin],
  props: {
    adjudicators: Array,
    position: String,
    debateId: Number
  },
  computed: {
    isIncomplete: function () {
      if (this.position === "C" && this.adjudicators.length === 0) {
        return true
      } else if (this.position === "P" && Math.abs(this.adjudicators.length % 2) == 1) {
        return true
      } else {
        return false
      }
    },
    adjudicatorsOrderedByScore: function() {
      return _.orderBy(this.adjudicators, 'score', ['desc'])
    }
  },
  components: {
    'DebateAdjudicator': DebateAdjudicator
  },
  methods: {
    handleDrop(event) {
      this.$dispatch('set-adj-panel', this.debateId, this.position)
    },
    propogateSetAdj(info) {
      console.log('setDraggedAdj positiondroppable');
      this.$emit('propogate-set-adj', info)
    },
    propogateUnsetAdj() {
      console.log('unsetDraggedAdj positiondroppable');
      this.$emit('propogate-unset-adj')
    }
  }
}
</script>