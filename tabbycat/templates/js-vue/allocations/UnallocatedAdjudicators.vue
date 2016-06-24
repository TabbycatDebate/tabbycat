<style>
.vue-droppable {
  min-height: 0;
}
</style>

<template>

  <nav
    v-on:dragover.prevent
    v-on:dragenter="handleDragEnter"
    v-on:dragleave="handleDragLeave"
    v-on:drop="handleDrop"
    v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
    class="navbar navbar-default navbar-fixed-bottom vue-droppable">

    <adjudicator-draggable
      v-for="adj in adjudicators | orderBy 'score' -1"
      :adj="adj">
    </adjudicator-draggable>

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
  },
  methods: {
    receiveDrop: function(ev) {
      console.log('Received an adj');
      this.$dispatch('moveToUnused', this.division);
    }
  }
}
</script>