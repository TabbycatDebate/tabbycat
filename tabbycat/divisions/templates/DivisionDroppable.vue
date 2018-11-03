<template>
  <div :class="['card', { 'panel-danger': hasEvenNumbers }]">

    <div class="card-body text-center pt-2 p-0">
      <h5 class="card-title">
        D{{ division.name }} <small>({{ teams.length }} teams)</small>
      </h5>

      <droppable-generic :assignment-id="division.id"
                         :extra-css="'card-body division-droppable'">
        <draggable-team v-for="team in teams" :round-info="roundInfo"
                        :key="team.id" :team="team">
        </draggable-team>
      </droppable-generic>

      <div class="panel-footer division-footer">
        <select name="select" class="custom-select custom-select-sm"
                v-model="division.venue_category"  v-if="vcs.length > 0">
          <option></option>
          <option v-for="vc in vcs" :value="vc.id" :key="vc.id">
            At {{ vc.name }} (capacity for {{ vc.total_capacity }} teams)
          </option>
        </select>
      </div>

    </div>

  </div>
</template>

<script>
import DroppableGeneric from '../../templates/draganddrops/DroppableGeneric.vue'
import LegacyDraggableTeam from '../../templates/draganddrops/LegacyDraggableTeam.vue'
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  components: { DroppableGeneric, LegacyDraggableTeam },
  props: ['division', 'vcs', 'teams', 'saveVenueCategoryUrl', 'roundInfo'],
  computed: {
    hasEvenNumbers: function () {
      return (this.teams.length % 2) === 1
    },
    venueCategory: function () {
      return this.division.venue_category
    },
  },
  watch: {
    venueCategory: function (val) {
      const payload = { venueCategory: val, division: this.division.id }
      const message = `Assigning division ${this.division} to ${val}`
      this.ajaxSave(this.saveVenueCategoryUrl, payload, message, null, null, null)
    },
  },
}
</script>
