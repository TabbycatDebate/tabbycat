<template>
  <div class="col-md-12 draw-container">

    <div class="row nav-pills">
      <a class="btn btn-primary " :href="roundInfo.backUrl">
        <span class="glyphicon glyphicon-chevron-left"></span> Back to Draw
      </a>
      <auto-save-counter :css="'btn-md pull-right'"></auto-save-counter>
    </div>

    <div class="row">
      <div class="mb-3" id="messages-container"></div>
    </div>

    <div class="mb-3">
      <draw-header :positions="positions"  @resort="updateSorting"
                   :sort-key="sortKey" :sort-order="sortOrder">
        <template slot="hteams">
          <div class="vue-sortable thead flex-cell flex-12 vue-droppable-container"
               v-for="position in positions" @click="updateSorting(position.side)"
               data-toggle="tooltip" :title="'The ' + position.full + ' team'">
            <span>{{ position.abbr }}</span>
            <span :class="sortClasses(position.full)"></span>
          </div>
        </template>
      </draw-header>
      <debate v-for="debate in dataOrderedByKey"
              :debate="debate" :key="debate.id" :round-info="roundInfo">
        <template v-for="dt in debate.debateTeams">
          <div class="draw-cell droppable-cell flex-12 vue-droppable-container"
               :slot="'s-' + dt.side">
            <droppable-generic :assignment-id="debate.id"
                               :assignment-position="dt.side" :locked="debate.locked">
              <draggable-team v-if="dt.team" :team="dt.team"
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

    <slide-over :subject="slideOverSubject"></slide-over>

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
    findDebateTeamInDebateByTeam(team, debate) {
      var debateTeam = _.find(debate.debateTeams, function(dt) {
        if (dt.team !== null) {
          return dt.team.id === team.id
        } else {
          return false
        }
      });
      return debateTeam
    },
    findDebateTeamInDebateBySide(side, debate) {
      var debateTeam = _.find(debate.debateTeams, function(dt) {
        return dt.side === side
      });
      return debateTeam
    },
    moveToDebate(payload, assignedId, assignedPosition) {
      if (payload.debate === assignedId) {
        var team = this.allTeamsById[payload.team]
        var debate = this.debatesById[payload.debate]
        var fromPosition = this.findDebateTeamInDebateByTeam(team, debate)
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
