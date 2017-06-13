<template>

  <div
    v-on:dragover.prevent
    v-on:dragenter="dragEnter"
    v-on:dragleave="dragLeave"
    v-on:drop="drop"
    v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
    class="panel-body vue-droppable">

    <draggable-team
      v-for="team in teamsOrderedByCode"
      v-if="team.division === null"
      v-bind:key="team.id"
      :team="team"
      :save-division-at="saveDivisionAt">
    </draggable-team>

  </div>

</template>

<script>
import DraggableTeam from  '../draganddrops/DraggableTeam.vue'
import DroppableMixin from '../draganddrops/DroppableMixin.vue'
import _ from 'lodash'

export default {
  mixins: [DroppableMixin],
  components: {'DraggableTeam': DraggableTeam},
  props: {
    teams: Array,
    'save-division-at': {},
  },
  computed: {
    teamsOrderedByCode: function() {
      return _.orderBy(this.teams, 'institution__code', ['asc'])
    }
  },
  methods: {
    handleDrop: function(ev) {
      this.$dispatch('unassign-team-division', null);
    }
  }
}
</script>
