<template>
  <div class="d-flex border-bottom bg-white">
    <slot name="bracket">
      <div v-if="debateOrPanel.bracket" class="flex-1 flex-truncate d-flex p-2 border-right">
        <div class="align-self-center flex-fill text-center">
          {{ debateOrPanel.bracket }}
        </div>
      </div>
      <div v-else-if="debateOrPanel.bracket_min == debateOrPanel.bracket_max" class="flex-2 flex-truncate d-flex border-right">
        <div class="align-self-center flex-fill text-center">
          {{ debateOrPanel.bracket_min }}
        </div>
      </div>
      <div v-else class="flex-2 flex-truncate d-flex border-right">
        <div class="align-self-center flex-fill text-center">
          {{ debateOrPanel.bracket_min }}<span class="text-muted">-</span>{{ debateOrPanel.bracket_max }}
        </div>
      </div>
    </slot>
    <slot name="liveness">
      <div class="flex-1 flex-truncate border-right d-flex">
        <div class="align-self-center flex-fill text-center">{{ debateOrPanel.liveness }}</div>
      </div>
    </slot>
    <slot name="importance">
      <div class="flex-1 flex-truncate border-right border-left d-flex">
        <div class="align-self-center flex-fill text-center">{{ debateOrPanel.importance }}</div>
      </div>
    </slot>
    <slot name="venue">
      <div class="flex-8 flex-truncate border-right ">
        <span v-if="debateOrPanel.venue">{{ debateOrPanel.venue.display_name }}</span>
      </div>
    </slot>
    <slot name="teams">
      <div class="vc-bp-grid flex-12 flex-truncate" v-if="sides.length === 4">
        <div :class="['d-flex flex-truncate align-items-center py-1 px-2 border-right',
                      i < 2 ? 'border-bottom' : '']"
             v-for="(side, i) in sides">
          <div class="text-truncate small" v-if="debateOrPanel.teams">
            {{ debateOrPanel.teams[side].short_name }}
          </div>
        </div>
      </div>
      <div class="d-flex flex-column flex-6 flex-truncate" v-if="sides.length === 2">
        <div :class="['d-flex flex-fill align-items-center py-1 px-2 border-right',
                      i % 2 === 0 ? 'border-bottom' : '']"
             v-for="(side, i) in sides">
          <div class="text-truncate small" v-if="debateOrPanel.teams">
            <span v-if="debateOrPanel.teams[side]">{{ debateOrPanel.teams[side].short_name }}</span>
            <span v-else class="text-danger text-uppercase">no {{ side }} team</span>
          </div>
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
