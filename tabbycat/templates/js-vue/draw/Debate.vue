<template>
  <div class="draw-row">

    <div class="draw-cell flex-1" data-toggle="tooltip" v-bind:title="'Debate is in the ' + debate.bracket + ' bracket'">
      {{ debate.bracket }}
    </div>

    <div class="draw-cell flex-1" data-toggle="tooltip">
      <!-- v-bind:title="liveness + ' break categories are live'" -->
        ?
    </div>

    <div class="draw-cell flex-1">
      <slot name="simportance">
        {{ debate.importance }}
      </slot>
    </div>

    <div class="draw-cell flex-2">
      <slot name="svenue">
        <span v-if="debate.venue">{{ debate.venue.name }}</span>
      </slot>
    </div>

    <template v-for="(team, index) in debate.teams">
      <div class="draw-cell flex-3">
        <slot :name="'sposition' + index">
          {{ team.short_name }}
        </slot>
      </div>
    </template>

    <div class="draw-cell flex-6">
      <slot name="spanel">
        <div>
          <span v-for="panellist in debate.panel">
            {{ panellist.adjudicator.name }} ({{ panellist.position }}),
          </span>
        </div>
      </slot>
    </div>

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