<style>
  .division-droppable {
    min-height: 66px;
    padding: 5px;
  }
</style>

<template>

  <div class="panel-body division-droppable"
    v-on:dragover.prevent
    v-on:drop="receiveTeam"
    v-on:dragenter="handleDragEnter"
    v-on:dragleave="handleDragLeave"
    v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
    data-id="{{ division.id }}">
    <template v-for="team in teams" track-by="id">
      <team-draggable :team="team" :vg="division.venue_group" :save-division-at="saveDivisionAt"></team-draggable>
    </template>
  </div>

</template>

<!-- Division Droppable Component Behaviour -->
<script>
import DroppableMixin from '../mixins/DroppableMixin.vue'
import TeamDraggable from  './TeamDraggable.vue'

export default {
  mixins: [DroppableMixin],
  props: {
    'division': {},
    'vgs': {},
    'teams': {},
    'save-vg-at': {},
    'save-division-at': {},
    'isDroppable': { default: false },
    'dragCounter': { default: 0 }
  },
  watch: {
    'division.venue_group': function (newVal, oldVal) {
      var vg_id = this.division.venue_group;
      var division_id = this.division.id;
      $.ajax({
          url: this.saveVgAt,
          type: "POST",
          data: {
            'venueGroup': vg_id,
            'division': division_id,
          },
          success:function(response){
            console.log('Saved division ' + division_id + ' to venue group ' + vg_id)
          },
          error:function (xhr, textStatus, thrownError){
            alert('Failed to save a division ' + division_id + '\s venue group change')
          }
      });
    },
  },
  computed: {
    // a computed getter
    hasEvenNumbers: function () {
      // `this` points to the vm instance
      return (this.teams.length % 2) == 1;
    }
  },
  components: {
    'TeamDraggable': TeamDraggable
  },
  methods: {
    receiveTeam: function(ev) {
      // This calls up to the parent component
      console.log('child component (' + this.division.id + ') received a team');
      this.$dispatch('assign-team-to-division', this.division);
      this.isDroppable = false;
      this.dragCounter = 0;
    }
  }
}
</script>
