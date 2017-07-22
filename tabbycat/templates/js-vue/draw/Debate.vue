<template>
  <div class="draw-row">

    <div class="draw-cell flex-1 flex-horizontal-center">
      {{ debate.bracket }}
    </div>

    <div class="draw-cell flex-1 flex-horizontal-center">
      {{ debate.liveness }}
    </div>

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

    <template v-for="position in roundInfo.positions">
      <slot :name="'s-' + position.full">
        <div class="draw-cell flex-6 draw-team-cell">
          <draw-team v-if="debate.teams[position.full]"
                     :team="debate.teams[position.full]"></draw-team>
        </div>
      </slot>
    </template>

    <slot name="spanel">
      <div class="draw-cell flex-12">
        <div><!-- Need a container else they align -->
          <draw-adjudicator v-for="panellist in debate.panel"
            :adjudicator="panellist.adjudicator"
            :position="panellist.position"
            :key="panellist.adjudicator.id">
          </draw-adjudicator>
        </div>
      </div>
    </slot>

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
