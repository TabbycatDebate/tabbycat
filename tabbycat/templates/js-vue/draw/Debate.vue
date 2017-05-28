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
        <div class="draw-cell flex-6">
          {{ team.short_name }}
        </div>
      </slot>
    </template>

    <slot name="spanel">
      <div class="draw-cell flex-12">
        <div><!-- Need a container else they align -->
          <span v-for="panellist in debate.panel">
            {{ panellist.adjudicator.name }} ({{ panellist.position }}),
          </span>
        </div>
      </div>
    </slot>

  </div>
</template>

<script>

export default {
  components: {
  },
  mixins: [
  ],
  props: {
    debate: Object,
  },
  computed: {
  },
  events: {
  },
  methods: {
  },
}

</script>