<template>
  <div class="draw-row">

    <slot name="sbracket" v-if="roundInfo.roundIsPrelim">
      <div class="draw-cell flex-1 flex-horizontal-center">
        {{ debate.bracket }}
      </div>
    </slot>

    <slot name="sliveness" v-if="roundInfo.roundIsPrelim && roundInfo.teamsInDebate !== 'bp'">
      <div class="draw-cell flex-1 flex-horizontal-center">
        {{ debate.liveness }}
      </div>
    </slot>

    <slot name="simportance">
      <div class="draw-cell flex-1 flex-horizontal-center">
        {{ debate.importance }}
      </div>
    </slot>

    <slot name="svenue">
      <div class="draw-cell flex-6">
        <draw-venue :venue="debate.venue"></draw-venue>
      </div>
    </slot>

    <template v-for="position in roundInfo.teamPositions">
      <slot :name="'s-' + position">
        <div class="draw-cell flex-6 draw-team-cell">
          <draw-team v-if="findTeamInDebateBySide(position, debate)"
                     :team="findTeamInDebateBySide(position, debate)"></draw-team>
        </div>
      </slot>
    </template>

    <slot name="spanel">
      <div class="draw-cell flex-12">
        <div class="small ml-2"><!-- Need a container else they align -->
          <draw-adjudicator v-for="da in debate.debateAdjudicators"
            :adjudicator="da.adjudicator"
            :position="da.position"
            :key="da.adjudicator.id">
          </draw-adjudicator>
        </div>
      </div>
    </slot>

    <slot name="sextra"></slot>

  </div>
</template>

<script>
import DrawTeam from '../draw/DrawTeam.vue'
import DrawVenue from '../draw/DrawVenue.vue'
import DrawAdjudicator from '../draw/DrawAdjudicator.vue'
import SlideOverSubjectMixin from '../../info/SlideOverSubjectMixin.vue'
import FindDebateTeamMixin from '../draw/FindDebateTeamMixin.vue'
import _ from 'lodash'

export default {
  components: {DrawTeam, DrawVenue, DrawAdjudicator},
  mixins: [SlideOverSubjectMixin, FindDebateTeamMixin],
  props: { debate: Object, roundInfo: Object},
  methods: {
    findDebateTeamInDebateBySide(side, debate) { // Used in Edit Matchups
      var debateTeam = _.find(debate.debateTeams, function(dt) {
        return dt.side === side
      });
      if (!_.isUndefined(debateTeam)) {
        return debateTeam
      } else {
        return false
      }
    },
  }
}
</script>
