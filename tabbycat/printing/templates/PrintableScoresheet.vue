<script setup>
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import PrintableTeamScores from './PrintableTeamScores.vue'

defineProps({
  ballot: Object,
  roundInfo: Object,
  ordinals: Array,
})

const { gettext } = useDjangoI18n()
</script>

<template>
  <div class="db-flex-column db-flex-item-1">
    <section class="db-margins-m db-flex-row db-flex-item-7">
      <printable-team-scores
        :dt="ballot.debateTeams[0]"
        :round-info="roundInfo"
        :ordinals="ordinals"
      />
      <div class="db-item-gutter" />
      <printable-team-scores
        :dt="ballot.debateTeams[1]"
        :round-info="roundInfo"
        :ordinals="ordinals"
      />
    </section>
    <section
      v-if="roundInfo.isBP"
      class="db-margins-m db-flex-row db-flex-item-7"
    >
      <printable-team-scores
        :dt="ballot.debateTeams[2]"
        :round-info="roundInfo"
        :ordinals="ordinals"
      />
      <div class="db-item-gutter" />
      <printable-team-scores
        :dt="ballot.debateTeams[3]"
        :round-info="roundInfo"
        :ordinals="ordinals"
      />
    </section>

    <section
      v-if="!roundInfo.isBP"
      class="db-margins-m db-bordered db-flex-row db-flex-item-1"
    >
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <!-- Aff holder -->
        <div
          class="db-flex-item db-align-vertical-center db-flex-static
                    db-vertical-center-text small"
        >
          {{ gettext('Which team won the debate:') }}
        </div>
        <div class="db-flex-item db-fill-in" />
      </div>
      <div class="db-item-gutter" />
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <!-- Aff holder -->
        <div
          class="db-align-vertical-center db-flex-item db-flex-static
                    db-vertical-center-text small"
        >
          {{ gettext('By how many points did they win:') }}
        </div>
        <div class="db-flex-item db-fill-in" />
      </div>
    </section>

    <section
      v-if="roundInfo.showInfo"
      class="db-margins-m db-bordered db-flex-row db-flex-item-1"
    >
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <!-- Aff holder -->
        <div class="db-flex-item db-align-vertical-center db-flex-static db-vertical-center-text">
          {{ roundInfo.infoText }}
        </div>
      </div>
    </section>
  </div>
</template>
