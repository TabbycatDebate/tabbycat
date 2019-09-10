<template>
  <div class="db-flex-column db-flex-item-1">

    <section class="db-margins-m db-flex-row db-flex-item-7">
      <printable-team-scores :dt="ballot.debateTeams[0]" :round-info="roundInfo" :ordinals="ordinals">
      </printable-team-scores>
      <div class="db-item-gutter"></div>
      <printable-team-scores :dt="ballot.debateTeams[1]" :round-info="roundInfo" :ordinals="ordinals">
      </printable-team-scores>
    </section>
    <section class="db-margins-m db-flex-row db-flex-item-7" v-if="roundInfo.isBP">
      <printable-team-scores :dt="ballot.debateTeams[2]" :round-info="roundInfo" :ordinals="ordinals">
      </printable-team-scores>
      <div class="db-item-gutter"></div>
      <printable-team-scores :dt="ballot.debateTeams[3]" :round-info="roundInfo" :ordinals="ordinals">
      </printable-team-scores>
    </section>

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="!roundInfo.isBP">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row"><!-- Aff holder -->
        <div class="db-flex-item db-align-vertical-center db-flex-static
                    db-vertical-center-text small"
             v-text="gettext('Which team won the debate:')"></div>
        <div class="db-flex-item db-fill-in">
        </div>
      </div>
      <div class="db-item-gutter"></div>
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row"><!-- Aff holder -->
        <div class="db-align-vertical-center db-flex-item db-flex-static
                    db-vertical-center-text small"
             v-text="gettext('By how many points did they win:')"></div>
        <div class="db-flex-item db-fill-in">
        </div>
      </div>
    </section>

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="roundInfo.showInfo">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row"><!-- Aff holder -->
        <div class="db-flex-item db-align-vertical-center db-flex-static db-vertical-center-text">
          {{ roundInfo.infoText }}
        </div>
      </div>
    </section>

  </div>
</template>

<script>
import PrintableTeamScores from './PrintableTeamScores.vue'

export default {
  props: ['ballot', 'roundInfo', 'ordinals'],
  components: { PrintableTeamScores },
}
</script>
