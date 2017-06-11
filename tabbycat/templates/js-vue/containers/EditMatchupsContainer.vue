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
        <template v-for="position in roundInfo.positions">
          <div class="draw-cell flex-8 vue-droppable-container" :slot="'s-' + position">
            <droppable-generic :assignment-id="debate.id"
                               :assignment-position="position" :locked="debate.locked">
              <draggable-team v-if="debate.teams[position]"
                              :team="debate.teams[position]"
                              :debate-id="debate.id" :locked="debate.locked"></draggable-team>
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
import TeamMovingMixin from '../ajax/TeamMovingMixin.vue'
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import DraggableTeam from '../draganddrops/DraggableTeam.vue'
import _ from 'lodash'

export default {
  mixins: [TeamMovingMixin, DrawContainerMixin],
  components: { DraggableTeam },
  computed: {
    unallocatedTeamsByWins: function() {
      return _.reverse(_.sortBy(this.unallocatedItems, ['wins']))
    },
    allTeamsById: function() {
      return _.keyBy(this.teams.concat(this.unallocatedItems), 'id')
    },
  },
  methods: {
    moveToDebate(payload, assignedId, assignedPosition) {
      if (payload.debate === assignedId) {
        var fromPosition = _.findKey(this.debatesById[payload.debate].teams,
                                     this.allTeamsById[payload.team])
        if (assignedPosition === fromPosition) {
          return // Moving to same debate/position; do nothing
        }
      }
      this.saveMove(payload.team, payload.debate, assignedId, assignedPosition)
    },
    moveToUnused(payload) {
      if (_.isUndefined(payload.debate)) {
        return // Moving to unused from unused; do nothing
      }
      this.saveMove(payload.team, payload.debate)
    }
  },
}

</script>
