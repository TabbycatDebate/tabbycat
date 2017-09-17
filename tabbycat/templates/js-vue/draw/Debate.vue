<template>
  <div class="draw-row">

    <slot name="sbracket">
      <div class="draw-cell flex-1 flex-horizontal-center">
        {{ debate.bracket }}
      </div>
    </slot>

    <slot name="sliveness">
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

    <template v-for="dt in debate.debateTeams">
      <slot :name="'s-' + dt.side">
        <div class="draw-cell flex-6 draw-team-cell">
          <draw-team v-if="dt.team" :team="dt.team"></draw-team>
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
import _ from 'lodash'

export default {
  components: {DrawTeam, DrawVenue, DrawAdjudicator},
  mixins: [SlideOverSubjectMixin],
  props: { debate: Object, roundInfo: Object},
}
</script>
