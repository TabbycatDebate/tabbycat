<template>

  <div
    v-on:dragover.prevent
    v-on:dragenter="dragEnter"
    v-on:dragleave="dragLeave"
    v-on:drop="drop"
    v-bind:class="['vue-droppable', {
        'panel-incomplete': isIncomplete,
        'vue-is-drag-enter': isDroppable,
        'flex-1': position !== 'P',
        'flex-2': position === 'P'
    }]"
    class="">

    <debate-adjudicator
      v-for="adj in adjudicators | orderBy 'score' -1"
      :adjorteam="adj"
      :position="position"
      :debate-id="debateId">
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