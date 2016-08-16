<template>

  <div
    v-on:dragover.prevent
    v-on:dragenter="dragEnter"
    v-on:dragleave="dragLeave"
    v-on:drop="drop"
    v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
    class="panel-body vue-droppable">

    <team-draggable
      v-for="team in teams | orderBy 'institution__code'"
      v-if="team.division === null"
      track-by="id"
      :team="team"
      :save-division-at="saveDivisionAt">
    </team-draggable>

  </div>

</template>

<script>
import TeamDraggable from  '../draganddrops/TeamDraggable.vue'
import DroppableMixin from '../mixins/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  props: {
    teams: Array,
    'save-division-at': {},
  },
  components: {
    'TeamDraggable': TeamDraggable
  },
  methods: {
    handleDrop: function(ev) {
      this.$dispatch('unassign-team-division', null);
    }
  }
}
</script>