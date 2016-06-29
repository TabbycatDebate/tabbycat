<template>

  <nav
    v-on:dragover.prevent
    v-on:dragenter="handleDragEnter"
    v-on:dragleave="handleDragLeave"
    v-on:drop="handleDrop"
    v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
    class="navbar navbar-default navbar-fixed-bottom vue-droppable">

    <debate-adjudicator
      v-for="adj in adjudicators | orderBy 'score' -1"
      :adj="adj"
      :current-conflict-highlights="currentConflictHighlights"
      :current-histories-highlights="currentHistoriesHighlights">
    </debate-adjudicator>

  </nav>

</template>

<script>
import DebateAdjudicator from './DebateAdjudicator.vue'
import DroppableMixin from '../mixins/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  props: {
    adjudicators: Array,
    currentConflictHighlights: Object,
    currentHistoriesHighlights: Array,
  },
  components: {
  'DebateAdjudicator': DebateAdjudicator
  },
  methods: {
    receiveDrop: function(ev) {
      console.log('Received an adj');
      this.$dispatch('moveToUnused', this.division);
    }
  }
}
</script>