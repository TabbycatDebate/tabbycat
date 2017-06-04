<template>
  <div class="draw-row">

    <div class="draw-cell flex-1" data-toggle="tooltip" v-bind:title="'Debate is in the ' + debate.bracket + ' bracket'">
      {{ debate.bracket }}
    </div>

    <div class="draw-cell flex-1" data-toggle="tooltip">
      <!-- v-bind:title="liveness + ' break categories are live'" -->
        ?
    </div>

    <slot name="simportance">
      <div class="draw-cell flex-1">
        {{ debate.importance }}
      </div>
    </slot>

    <slot name="svenue">
      <div class="draw-cell flex-2">
        <span v-if="debate.venue">{{ debate.venue.name }}</span>
      </div>
    </slot>

    <template v-for="(team, index) in debate.teams">
      <slot :name="'sposition' + index">
        <draw-team :team="team"></draw-team>
      </slot>
    </template>

    <slot name="spanel">
      <div class="draw-cell flex-12">
        <div><!-- Need a container else they align -->
          <draw-adjudicator v-for="panellist in debate.panel"
                            :adjudicator="panellist.adjudicator"
                            :position="panellist.position"></draw-adjudicator>
        </div>
      </div>
    </slot>

  </div>
</template>

<script>
import DrawTeam from '../draw/DrawTeam.vue'
import DrawAdjudicator from '../draw/DrawAdjudicator.vue'
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'

export default {
  components: {DrawTeam, DrawAdjudicator},
  mixins: [SlideOverSubjectMixin],
  props: {
    debate: Object,
  },
}
</script>