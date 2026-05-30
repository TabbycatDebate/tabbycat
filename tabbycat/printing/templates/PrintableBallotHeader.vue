<script setup>
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'


const props = defineProps({
  ballot: Object,
  roundInfo: Object,
})

const { gettext, tct } = useDjangoI18n()

</script>

<template>
  <header class="db-margins-m db-flex-row h5 mb-2 mt-3">
    <div class="db-flex-item">
      <span v-if="!roundInfo.votingBallots && !ballot.target">
        {{ tct('%s from %s', [roundInfo.round, ballot.author]) }}
      </span>
      <span v-if="roundInfo.votingBallots">
        {{ tct('%s from %s', [roundInfo.round, ballot.author]) }}
      </span>
      <span v-if="ballot.target">
        <span v-if="ballot.targetPosition === 'c' || ballot.targetPosition === 'o'">
          {{ tct('%s from %s on %s (Chair)', [roundInfo.round, ballot.author, ballot.target]) }}
        </span>
        <span v-if="ballot.targetPosition === 'p'">
          {{ tct('%s from %s on %s (Panellist)', [roundInfo.round, ballot.author, ballot.target]) }}
        </span>
        <span v-if="ballot.targetPosition === 't'">
          {{ tct('%s from %s on %s (Trainee)', [roundInfo.round, ballot.author, ballot.target]) }}
        </span>
        <span v-if="ballot.targetPosition === ''">
          {{ tct('%s from %s on %s (unknown position)', [roundInfo.round, ballot.author, ballot.target]) }}
        </span>
      </span>
    </div>

    <div
      v-if="ballot.venue === '' || ballot.venue === null"
      class="ml-auto"
    >
      <span v-if="ballot.barcode">
        {{ tct('ID %s,', [ballot.barcode]) }}
      </span>
      <span>{{ gettext('Room:') }}</span>
      <span
        class="db-padding-horizontal db-fill-in"
        style="width: 232px; margin: 0 3px 0 5px; display: inline-block"
      />
    </div>

    <div
      v-else
      class="ml-auto "
    >
      <span v-if="ballot.barcode">{{ tct('ID %s,', [ballot.barcode]) }}</span>
      {{ ballot.venue.display_name }}
    </div>
  </header>
</template>
