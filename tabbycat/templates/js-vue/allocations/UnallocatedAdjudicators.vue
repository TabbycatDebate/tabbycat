<template>

  <nav
    v-on:dragover.prevent
    v-on:dragenter="dragEnter"
    v-on:dragleave="dragLeave"
    v-on:drop="drop"
    v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
    class="navbar navbar-default navbar-fixed-bottom vue-droppable unallocated-adjs">

    <debate-adjudicator
      v-for="adj in adjudicators | orderBy 'score' -1"
      v-if="!adj.allocated"
      :adj="adj">
    </debate-adjudicator>

  </nav>

</template>

<script>
import DebateAdjudicator from './DebateAdjudicator.vue'
import DroppableMixin from '../mixins/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  props: {
    adjudicators: Object
  },
  components: {
  'DebateAdjudicator': DebateAdjudicator
  },
  methods: {
    handleDrop: function(ev) {
      this.$dispatch('set-adj-unused');
    }
  }
}
</script>