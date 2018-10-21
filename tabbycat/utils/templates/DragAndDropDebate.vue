<template>
  <div class="d-flex border-bottom bg-white">
    <slot name="bracket">
      <div v-if="debateOrPanel.bracket" class="flex-1 d-flex p-2 border-right">
        <div class="align-self-center flex-fill text-center">
          {{ debateOrPanel.bracket }}
        </div>
      </div>
      <div v-else class="flex-2 d-flex border-right">
        <div class="align-self-center flex-fill text-center">
          {{ debateOrPanel.bracket_min }}<span class="text-muted">-</span>{{ debateOrPanel.bracket_max }}
        </div>
      </div>
    </slot>
    <slot name="liveness">
      <div class="flex-1 border-right d-flex">
        <div class="align-self-center flex-fill text-center">{{ debateOrPanel.liveness }}</div>
      </div>
    </slot>
    <slot name="importance">
      <div class="flex-1 border-right border-left d-flex">
        <div class="align-self-center flex-fill text-center">{{ debateOrPanel.importance }}</div>
      </div>
    </slot>
    <slot name="venue">
      <div class="flex-8 border-right ">
        <span v-if="debateOrPanel.venue">{{ debateOrPanel.venue.display_name }}</span>
      </div>
    </slot>
    <slot name="teams">
      <div class="flex-6 d-flex flex-column">
        <div class="flex-1 d-flex p-2 align-items-center"
             v-for="team in debateOrPanel.teams">
          {{ team.short_name }}
        </div>
      </div>
    </slot>
    <slot name="adjudicators">
      <div class="flex-16">
        <span v-for="adj in debateOrPanel.adjudicators.C">{{ adj.name }} (C),</span>
        <span v-for="adj in debateOrPanel.adjudicators.P">{{ adj.name }}</span>
        <span v-for="adj in debateOrPanel.adjudicators.T">{{ adj.name }} (T)</span>
      </div>
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
