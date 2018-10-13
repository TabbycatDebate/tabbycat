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
    <slot name="teams">
      — TEAMS
    </slot>
    <slot name="adjudicators">
      — ADJS
    </slot>
  </div>
</template>

<script>
// Provides the base template for a debate object used across all edit adjudicator screens
// Uses slots so that parent components can override them with custom components for editing the
// specific type of data they are responsible for
export default {
  props: ['debateOrPanel', 'ws'],
}
</script>
