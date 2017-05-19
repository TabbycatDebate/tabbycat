<template>
  <div class="row flex-horizontal">

    <div class="flex-cell flex-vertical-center bordered-bottom">
      <div class="flex-2 text-center" data-toggle="tooltip" v-bind:title="'Debate is in the ' + debate.bracket + ' bracket'">
        {{ debate.bracket }}
      </div>
    </div>

    <div class="flex-cell flex-vertical-center bordered-bottom">
      <div class="flex-2 text-center" data-toggle="tooltip" title="">
        <slot name="venue">{{ debate.venue.name }}</slot>
      </div>
    </div>

    <template v-for="(team, index) in debate.teams">
      <div class="flex-cell debate-team flex-vertical-center bordered-bottom">
        <div class="flex-2 text-center" data-toggle="tooltip" title="test">
          <slot :name="index">
            {{ team.short_name }}
          </slot>
        </div>
      </div>
    </template>

    <div class="flex-cell flex-vertical-center bordered-bottom">
      <div class="flex-6 text-center" data-toggle="tooltip" title="test">
        <span v-for="panellist in debate.panel">
          {{ panellist.adjudicator.name }} ({{ panellist.position }}),
        </span>
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