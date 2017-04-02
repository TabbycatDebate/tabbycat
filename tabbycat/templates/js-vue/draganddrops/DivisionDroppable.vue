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
          :vc="division.venue_category"
          :vc-name="division.venue_category__name"
          :save-division-at="saveDivisionAt">
        </team-draggable>
      </template>

    </div>

    <div class="panel-footer division-footer">
      <select name="select" class="form-control btn-sm" v-model="division.venue_category"  v-if="vcs.length > 0">
        <option value=""></option>
        <option v-for="vc in vcs" value="{{ vc.id }}" v-bind:value="vc.id">
          At {{ vc.name }} (capacity for {{ vc.total_capacity }} teams)
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
    'vcs': {},
    'teams': {},
    'save-vc-at': {},
    'save-division-at': {},
    'isDroppable': { default: false },
    'dragCounter': { default: 0 }
  },
  watch: {
    'division.venue_category': function (newVal, oldVal) {
      var vc_id = this.division.venue_category;
      var division_id = this.division.id;
      $.ajax({
          url: this.saveVcAt,
          type: "POST",
          data: {
            'venueCategory': vc_id,
            'division': division_id,
          },
          success:function(response){
            console.log('Saved division ' + division_id + ' to venue venue_category ' + vc_id)
          },
          error:function (xhr, textStatus, thrownError){
            alert('Failed to save a division ' + division_id + '\s venue venue_category change')
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
