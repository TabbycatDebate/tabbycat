<template>
  <div class="draw-row">

    <div class="draw-cell">
      <div class="flex-2 text-center" data-toggle="tooltip" v-bind:title="'Debate is in the ' + debate.bracket + ' bracket'">
        {{ debate.bracket }}
      </div>
    </div>

    <div class="draw-cell">
      <div class="flex-1 text-center" data-toggle="tooltip">
        <!-- v-bind:title="liveness + ' break categories are live'" -->
        ?
      </div>
    </div>

    <div class="draw-cell">
      <div class="flex-1">
        <slot name="importance">
          {{ debate.importance }}
        </slot>
      </div>
    </div>

    <div class="draw-cell">
      <div class="flex-2">
        <slot name="venue">{{ debate.venue.name }}</slot>
      </div>
    </div>

    <template v-for="(team, index) in debate.teams">
      <div class="draw-cell">
        <div class="flex-2">
          <slot :name="index">
            {{ team.short_name }}
          </slot>
        </div>
      </div>
    </template>

    <div class="draw-cell">
      <div class="flex-6 text-center">
        <slot name="panel">
          <span v-for="panellist in debate.panel">
            {{ panellist.adjudicator.name }} ({{ panellist.position }}),
          </span>
        </slot>
      </div>
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