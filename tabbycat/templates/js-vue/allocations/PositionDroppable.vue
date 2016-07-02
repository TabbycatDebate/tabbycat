<template>

  <div
    v-on:dragover.prevent
    v-on:dragenter="dragEnter"
    v-on:dragleave="dragLeave"
    v-on:drop="drop"
    v-bind:class="['vue-droppable', {
        'panel-incomplete': isIncomplete,
        'vue-is-drag-enter': isDroppable,
        'flex-1': position === 'C',
        'flex-2': position !== 'C'
    }]"
    class="">

    <debate-adjudicator
      v-for="adj in adjudicators | orderBy 'score' -1"
      :adj="adj"
      :position="position"
      :debate-id="debateId"
      :current-conflict-highlights="currentConflictHighlights"
      :current-histories-highlights="currentHistoriesHighlights">
    </debate-adjudicator>

  </div>

</template>

<script>
import DebateAdjudicator from './DebateAdjudicator.vue'
import DroppableMixin from '../mixins/DroppableMixin.vue'

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
    }
  },
  components: {
    'DebateAdjudicator': DebateAdjudicator
  },
  methods: {
    'handleDrop': function(event) {
      this.$dispatch('set-adj-panel', this.debateId, this.position)
    }
  }
}
</script>