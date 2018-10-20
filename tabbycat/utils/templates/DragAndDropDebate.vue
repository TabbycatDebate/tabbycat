<template>
  <div>
    DEBATE {{ debateOrPanel.id }}
    <slot name="bracket">
      — BRACKET {{ debateOrPanel.bracket }}
    </slot>
    <slot name="liveness">
      — LIVENESS
    </slot>
    <slot name="importance">
      — IMPORTANCE: {{ debateOrPanel.importance }}
    </slot>
    <slot name="venue">
      — VENUE <span v-if="debateOrPanel.venue">{{ debateOrPanel.venue.display_name }}</span>
    </slot>
    <br>---------------
    <slot name="teams">
      <span v-for="(team, position) in debateOrPanel.teams">{{ team.short_name }} ({{ position }}),</span>
    </slot>
    <slot name="adjudicators">
      <span v-for="adj in debateOrPanel.adjudicators.C">{{ adj.name }} (C),</span>
      <span v-for="adj in debateOrPanel.adjudicators.P">{{ adj.name }}</span>
      <span v-for="adj in debateOrPanel.adjudicators.T">{{ adj.name }} (T)</span>
    </slot>
  </div>
</template>

<script>
// Provides the base template for a debate object used across all edit adjudicator screens
// Uses slots so that parent components can override them with custom components for editing the
// specific type of data they are responsible for
export default {
  props: ['debateOrPanel'],
}
</script>
