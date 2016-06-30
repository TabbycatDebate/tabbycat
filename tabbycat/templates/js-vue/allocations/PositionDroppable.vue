<template>

    <div
      v-on:dragover.prevent
      v-on:dragenter="handleDragEnter"
      v-on:dragleave="handleDragLeave"
      v-on:drop="setAdjPosition"
      v-bind:class="['vue-droppable', {
          'vue-is-drag-enter': isDroppable,
          'flex-1': position === 'C',
          'flex-2': position !== 'C'
      }]"
      class="">

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
    adjudicators: Array,
    position: String
  },
  components: {
    'DebateAdjudicator': DebateAdjudicator
  },
  methods: {
    'setAdjPosition': function(event) {
      console.log(this.position, event)
    }
  }
}
</script>