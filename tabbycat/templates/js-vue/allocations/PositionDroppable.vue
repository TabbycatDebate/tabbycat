<template>

    <div
      v-on:dragover.prevent
      v-on:dragenter="handleDragEnter"
      v-on:dragleave="handleDragLeave"
      v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
      class="vue-droppable">

      <debate-adjudicator
        v-for="adj in adjudicators | orderBy 'score' -1"
        :adj="adj">
      </debate-adjudicator>

    </div>

</template>

<script>
import DebateAdjudicator from './DebateAdjudicator.vue'
import DroppableMixin from '../mixins/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  props: {
    adjudicators: Array
  },
  components: {
    'DebateAdjudicator': DebateAdjudicator
  }
}
</script>