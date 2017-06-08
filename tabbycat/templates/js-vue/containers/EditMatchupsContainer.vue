<template>
  <div class="col-md-12 draw-container">

    <div class="row nav-pills">
      <a class="btn btn-default submit-disable" :href="roundInfo.backUrl">
        <span class="glyphicon glyphicon-chevron-left"></span> Back to Draw
      </a>
      <auto-save-counter :css="'btn-md pull-right'"></auto-save-counter>
    </div>

    <div class="row">
      <div class="vertical-spacing" id="messages-container"></div>
    </div>

    <div class="vertical-spacing">
      <draw-header :positions="roundInfo.positions">
        <template slot="hteams">
          <div class="thead flex-cell flex-8 vue-droppable-container" data-toggle="tooltip" title="test"
            v-for="position in roundInfo.positions">
            <span>{{ position }}</span>
          </div>
        </template>
      </draw-header>
      <debate v-for="debate in debates" :debate="debate" :key="debate.id" :round-info="roundInfo">
        <template v-for="(position, index) in roundInfo.positions">
          <div class="draw-cell flex-8 vue-droppable-container" :slot="'sposition' + index">
            <droppable-generic>
              <draggable-team v-if="debate.teams[index].team"
                :team="debate.teams[index].team" :debate-id="debate.id"></draggable-team>
            </droppable-generic>
          </div>
        </template>
      </debate>
    </div>

    <unallocated-items-container>
      <div v-for="unallocatedTeam in unallocatedTeamsByWins">
        <draggable-team :team="unallocatedTeam"> </draggable-team>
      </div>
    </unallocated-items-container>

    <slide-over-item :subject="slideOverItem"></slide-over-item>

  </div>
</template>

<script>
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import DraggableTeam from '../draganddrops/DraggableTeam.vue'
import _ from 'lodash'

export default {
  mixins: [DrawContainerMixin],
  components: { DraggableTeam },
  computed: {
    unallocatedTeamsByWins: function() {
      return _.reverse(_.sortBy(this.unallocatedItems, ['wins']))
    }
  },
  methods: {
    moveToUnused(payload) {
      if (_.isUndefined(payload.debate)) {
        return // Moving to unused from unused; do nothing
      }
      var draggedTeam = this.teamsById[payload.team]
      var dts = this.debatesById[payload.debate].teams // Convenience var
      // Make changes to the reactive property
      this.debatesById[payload.debate].teams = _.forEach(dts, function(dt) {
        // For each debate's debateTeams set the team to null if it matches
        if (dt.team === draggedTeam) { dt.team = null }
        return dt
      })
      this.unallocatedItems.push(draggedTeam) // Need to push; not append
    }
  },
}

</script>
