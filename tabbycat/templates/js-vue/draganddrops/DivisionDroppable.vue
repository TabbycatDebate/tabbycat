<template>

  <div class="panel panel-default" v-bind:class="{ 'panel-danger': hasEvenNumbers }">

    <div class="panel-heading text-center">
      <h5 class="panel-title">
        D{{ division.name }} <small>({{ teams.length }} teams)</small>
      </h5>
    </div>

    <div class="panel-body vue-droppable division-droppable"
      v-on:dragover.prevent
      v-on:drop="drop"
      v-on:dragenter="dragEnter"
      v-on:dragleave="dragLeave"
      v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
      :data-id="division.id">

      <template v-for="team in teams" track-by="id">
        <team-draggable
          :team="team"
          :vg="division.venue_group"
          :save-division-at="saveDivisionAt">
        </team-draggable>
      </template>

    </div>

    <div class="panel-footer division-footer">
      <select name="select" class="form-control btn-sm" v-model="division.venue_group"  v-if="vgs.length > 0">
        <option value=""></option>
        <option v-for="vg in vgs" value="{{ vg.id }}" v-bind:value="vg.id">
          At {{ vg.short_name }}
        </option>
      </select>
    </div>

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
    handleDrop: function(ev) {
      // This calls up to the parent component
      this.$dispatch('assign-team-to-division', this.division);
    }
  }
}
</script>
