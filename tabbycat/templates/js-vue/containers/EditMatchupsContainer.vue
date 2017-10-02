<template>
  <div class="draw-container">

    <div class="row page-navs">
      <div class="col d-flex justify-content-between">
        <a class="btn btn-outline-primary " :href="roundInfo.backUrl">
          <i data-feather="chevron-left"></i> Back to Draw
        </a>
        <auto-save-counter :css="'btn-md'"></auto-save-counter>
      </div>
    </div>

    <div class="row">
      <div class="col mb-2">

        <div class="card border-info text-info">
          <div class="card-body">
            This interface is intended to easily swap the positions of teams,
            as often required for final rounds. However it can be used to create
            new debates and edit matchups. This should be done with caution;
            edits to matchups will <em>remove any round results for the moved
            teams</em>. In general you should only use this on unreleased draws;
            and only then if you don't want a 'correct' draw.
            Note that changes to matchups will only be saved once
            <em>all slots are filled</em>. You can create new debates by
            dragging into the blank rows at the bottom, but debates cannot be
            deleted here — that requires going to the Edit Database area.
          </div>
        </div>

        <div id="messages-container"></div>

      </div>
    </div>

    <div class="row">
      <div class="col mb-3 mt-3">

          <draw-header :round-info="roundInfo"  @resort="updateSorting"
                       :sort-key="sortKey" :sort-order="sortOrder">

            <div slot="hbracket"></div>
            <div slot="hliveness"></div>
            <div slot="himportance"></div>
            <div slot="hvenue"></div>

            <template slot="hteams">
              <div class="vue-sortable thead flex-cell flex-12"
                   v-for="position in positions" @click="updateSorting(position.side)"
                   data-toggle="tooltip" :title="'The ' + position.full + ' team'">
                <span>{{ position.abbr }}</span>
                <span :class="sortClasses(position.full)"></span>
              </div>
            </template>

            <div slot="hpanel"></div>
            <div slot="hextra" class="vue-sortable thead flex-cell flex-8"
                 data-toggle="tooltip" title="Some types of draws (e.g.
                 out-rounds) do not specify the positions of each team at the
                 time of draw generation. Once a debate's sides have been
                 finalised its side status should be set as confirmed.">
              <span>Sides Status</span>
            </div>

          </draw-header>

          <debate v-for="debate in dataOrderedByKey"
                  :debate="debate" :key="debate.id" :round-info="roundInfo">

            <div slot="sbracket"></div>
            <div slot="sliveness"></div>
            <div slot="simportance"></div>
            <div slot="svenue"></div>

            <template v-for="position in roundInfo.teamPositions">
              <div class="draw-cell droppable-cell flex-12 vue-droppable-container"
                   :slot="'s-' + position">
                <droppable-generic :assignment-id="debate.id"
                                   :assignment-position="position" :locked="debate.locked">
                   <draggable-team v-if="findTeamInDebateBySide(position, debate)"
                                  :team="findTeamInDebateBySide(position, debate)"
                                  :debate-id="debate.id" :locked="debate.locked"
                                  :round-info="roundInfo"></draggable-team>
                </droppable-generic>
              </div>
            </template>

            <div slot="spanel"></div>
            <draw-sides-status slot="sextra" class="draw-cell flex-8"
                               :debate="debate" :save-url="saveSidesStatusUrl">
              {{ debate.confirmedSides }} Confirmed
            </draw-sides-status>

          </debate>

      </div>
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
import DrawSidesStatus from '../draw/DrawSidesStatus.vue'
import FindDebateTeamMixin from '../draw/FindDebateTeamMixin.vue'
import _ from 'lodash'

export default {
  mixins: [TeamMovingMixin, DrawContainerMixin, FindDebateTeamMixin],
  components: { DraggableTeam, DrawSidesStatus },
  props: ['saveSidesStatusUrl'],
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
