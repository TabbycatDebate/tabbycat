<template>
  <div :class="['panel panel-default', { 'panel-danger': hasEvenNumbers }]">

    <div class="panel-heading text-center">
      <h5 class="panel-title">
        D{{ division.name }} <small>({{ teams.length }} teams)</small>
      </h5>
    </div>

    <droppable-generic :assignment-id="division.id"
                       :extra-css="'panel-body division-droppable'">
      <draggable-team v-for="team in teams" :key="team.id":team="team">
      </draggable-team>
    </droppable-generic>

    <div class="panel-footer division-footer">
      <select name="select" class="form-control btn-sm"
              v-model="division.venue_category"  v-if="vcs.length > 0">
        <option value=""></option>
        <option v-for="vc in vcs" :value="vc.id">
          At {{ vc.name }} (capacity for {{ vc.total_capacity }} teams)
        </option>
      </select>
    </div>

  </div>
</template>

<script>
import DroppableGeneric from '../../templates/js-vue/draganddrops/DroppableGeneric.vue'
import DraggableTeam from  '../../templates/js-vue/draganddrops/DraggableTeam.vue'
import AjaxMixin from '../../templates/js-vue/ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  components: { DroppableGeneric, DraggableTeam },
  props: [ 'division', 'vcs', 'teams', 'saveVenueCategoryUrl'],
  computed: {
    hasEvenNumbers: function () {
      return (this.teams.length % 2) == 1;
    },
    venueCategory: function() {
      return this.division.venue_category
    }
  },
  watch: {
    venueCategory: function (val) {
      var payload = { 'venueCategory': val, 'division': this.division.id }
      var message = 'Assigning division ' + this.division + ' to ' + val
      this.ajaxSave(this.saveVenueCategoryUrl, payload, message, null, null, null)
    }
  },
}
</script>
