<template>
  <div class="d-flex border-bottom bg-white">
    <slot name="bracket">
      <div v-if="debateOrPanel.bracket >= 0" class="flex-2 flex-truncate d-flex border-right">
        <div class="align-self-center flex-fill text-center">
          {{ debateOrPanel.bracket }}
        </div>
      </div>
      <div v-else class="flex-2 flex-truncate d-flex border-right">
        <div class="align-self-center flex-fill text-center">
          <span v-if="debateOrPanel.bracket_min !== debateOrPanel.bracket_max">
            {{ debateOrPanel.bracket_min }}<span class="text-muted">-</span>{{ debateOrPanel.bracket_max }}
          </span>
          <span v-else>{{ debateOrPanel.bracket_min }}</span>
        </div>
      </div>
    </slot>
    <slot name="liveness">
      <div class="flex-1 flex-truncate border-right d-flex">
        <div class="align-self-center flex-fill text-center">{{ debateOrPanel.liveness }}</div>
      </div>
    </slot>
    <slot name="importance">
      <div class="flex-1 flex-truncate border-right d-flex">
        <div class="align-self-center flex-fill text-center">{{ debateOrPanel.importance }}</div>
      </div>
    </slot>
    <slot name="venue">
      <div class="flex-6 flex-truncate border-right align-self-center p-2 small">
        <span v-if="debateOrPanel.venue">{{ debateOrPanel.venue.display_name }}</span>
      </div>
    </slot>
    <slot name="teams">
      <div class="vc-bp-grid flex-12 flex-truncate" v-if="sides.length === 4">
        <div :class="['d-flex flex-truncate align-items-center']"
             v-for="side in sides" v-if="debateOrPanel.teams">
          <inline-team v-if="debateOrPanel.teams[side]" :debate-id="debateOrPanel.id"
                       :team="debateOrPanel.teams[side]"></inline-team>
          <span v-else class="text-danger text-uppercase">no {{ side }} team</span>
        </div>
      </div>
      <div class="d-flex flex-column flex-6 flex-truncate" v-if="sides.length === 2">
        <div :class="['d-flex flex-fill align-items-center']"
             v-for="side in sides">
          <inline-team v-if="debateOrPanel.teams[side]" :team="debateOrPanel.teams[side]"></inline-team>
          <span v-else class="text-danger text-uppercase">no {{ side }} team</span>
        </div>
      </div>
    </slot>
    <slot name="adjudicators">
      <div class="flex-16 align-self-center p-2 small">
        <span v-for="adj in debateOrPanel.adjudicators.C">{{ adj.name }} ⓒ, </span>
        <span v-for="adj in debateOrPanel.adjudicators.P">{{ adj.name }}, </span>
        <span v-for="adj in debateOrPanel.adjudicators.T">{{ adj.name }} ⓣ,</span>
      </div>
    </slot>
  </div>
</template>

<script>
// Provides the base template for a debate object used across all edit adjudicator screens
// Uses slots so that parent components can override them with custom components for editing the
// specific type of data they are responsible for
import InlineTeam from '../../draw/templates/InlineTeam.vue'

export default {
  components: { InlineTeam },
  props: ['debateOrPanel'],
  computed: {
    sides: function () {
      return this.$store.state.tournament.sides
    },
  },
}
</script>

<style scoped>
  .vc-bp-grid {
    display: inline-grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
  }
</style>
