<template>

  <nav class="navbar navbar-default navbar-fixed-bottom">
    <div
      v-on:dragover.prevent
      v-on:dragenter="handleDragEnter"
      v-on:dragleave="handleDragLeave"
      v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
      class="vue-droppable">

      <adjudicator-draggable
        v-for="adj in adjudicators | orderBy 'score' -1"
        :adj="adj">
      </adjudicator-draggable>

    </div>
  </nav>

</template>

<script>
import AdjudicatorDraggable from './AdjudicatorDraggable.vue'
import DroppableMixin from '../mixins/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  props: {
    adjudicators: Array
  },
  components: {
    'AdjudicatorDraggable': AdjudicatorDraggable
  }
}
</script>