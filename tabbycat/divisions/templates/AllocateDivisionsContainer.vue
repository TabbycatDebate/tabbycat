<template>
  <div class="draw-container">

    <div class="row divisions-holder">
      <div v-for="division in divisionsOrderedByName" :key="division.id"
           class="col-sm-3 col-md-3 col-lg-2">
        <division-droppable
          :division="division"
          :save-venue-category-url="saveVenueCategoryUrl"
          :teams="teamsInDivision(division.id)"
          :vcs="venueCategories">
        </division-droppable>
      </div>
    </div>

    <unallocated-items-container>
      <div v-for="team in unallocatedTeams">
        <draggable-team :team="team"></draggable-team>
      </div>
    </unallocated-items-container>

  </div>
</template>

<script>
import DivisionDroppable from  './DivisionDroppable.vue'
import UnallocatedItemsContainer from  '../../templates/js-vue/containers/UnallocatedItemsContainer.vue'
import DraggableTeam from  '../../templates/js-vue/draganddrops/DraggableTeam.vue'
import AjaxMixin from '../../templates/js-vue/ajax/AjaxMixin.vue'
import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  components: { DraggableTeam, DivisionDroppable, UnallocatedItemsContainer },
  props: ['teams', 'divisions', 'venueCategories',
          'saveDivisionsUrl', 'saveVenueCategoryUrl'],
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('unassign-draggable', this.moveToUnused)
    this.$eventHub.$on('assign-draggable', this.moveToDivision)
  },
  computed: {
    teamsById: function() {
      return _.keyBy(this.debateTeams, 'id')
    },
    divisionsOrderedByName: function() {
      return _.orderBy(this.divisions, 'name')
    },
    unallocatedTeams: function() {
      return _.filter(this.debateTeams, { 'division': null })
    }
  },
  methods: {
    teamsInDivision: function(divisionId) {
      return _.filter(this.debateTeams, { 'division': divisionId })
    },
    moveToDivision(payload, assignedId) {
      this.teamsById[payload.team].division = assignedId
      var payload = { 'team': payload.team, 'division': assignedId }
      var message = 'Assigning team ' + payload.team + ' to ' + assignedId
      this.ajaxSave(this.saveDivisionsUrl, payload, message, null, null, null)
    },
    moveToUnused(payload) {
      this.teamsById[payload.team].division = null
      var payload = { 'team': payload.team, 'division': null }
      var message = 'Assigning team ' + payload.team + ' to no division'
      this.ajaxSave(this.saveDivisionsUrl, payload, message, null, null, null)
    },
  }
}
</script>
