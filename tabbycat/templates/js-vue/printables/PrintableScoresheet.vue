<template>
  <div class="db-flex-column db-flex-item-1">

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1"
             v-if="ballot.panel && ballot.panel.length > 1">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
          Your panellists are
          <span v-for="(adj, i) in ballotsExcludingSelf">
            <span v-if="i !== 0">&nbsp;and</span>&nbsp;<strong>{{ adj.name }}</strong>
            <span v-if="adj.position === 'c'">(Chair, {{ adj.institution }})</span>
            <span v-if="adj.position === 'o'">(Solo Chair, {{ adj.institution }})</span>
            <span v-if="adj.position === 'p'">(Panellist, {{ adj.institution }})</span>
            <span v-if="adj.position === 't'">(Trainee, {{ adj.institution }})</span>
          </span>
        </div>
      </div>
    </section>

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1"
             v-if="roundInfo.hasMotions && !roundInfo.hasVetoes">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
          Motion:
        </div>
        <div class="db-flex-item db-align-vertical-center">
          <em>{{ motions[0].text }}</em>
        </div>
      </div>
    </section>

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1"
             v-if="roundInfo.hasMotions && roundInfo.hasVetoes">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div v-for="choice_type in ['Chosen Motion', 'Aff Veto', 'Neg Veto']" class="db-flex-item-1 db-flex-column">

          <div class="db-flex-item-2 db-align-horizontal-center db-align-vertical-end" v-html="choice_type"></div>
          <div class="db-flex-item-1 "></div>
          <div class="db-flex-item-2 db-flex-row">
            <div class="db-item-gutter"></div>
            <div v-for="motion in roundInfo.motions" class="db-align-horizontal-center db-align-vertical-start db-flex-item-1 db-center-text">
              <span class="db-fill-in">{{ motion.seq }}</span>
            </div>
            <div class="db-item-gutter"></div>
          </div>

        </div>
      </div>

      <div class="db-item-gutter"></div>
      <div class="db-flex-item-2 db-flex-row db-align-vertical-center">
        <template v-for="(motion, index) in roundInfo.motions">
          {{ motion.seq }}: {{ motion.text }}<br>
        </template>
      </div>

    </section>

    <section class="db-margins-m db-flex-row db-flex-item-7">
      <printable-team-scores :position="roundInfo.positions[0]" :speakers="ballot.affSpeakers"
                             :name="ballot.aff" :emoji="ballot.affEmoji" :round-info="roundInfo">
      </printable-team-scores>
      <div class="db-item-gutter"></div>
      <printable-team-scores :position="roundInfo.positions[1]" :speakers="ballot.negSpeakers"
                             :name="ballot.neg" :emoji="ballot.negEmoji" :round-info="roundInfo">
      </printable-team-scores>
    </section>

    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1"
             v-if="roundInfo.positions.length < 3">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row"><!-- Aff holder -->
        <div class="db-flex-item db-align-vertical-center db-flex-static db-vertical-center-text">
          Which team won the debate:
        </div>
        <div class="db-flex-item db-fill-in">
        </div>
      </div>
      <div class="db-item-gutter"></div>
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row"><!-- Aff holder -->
        <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
          By how many points did they win:
        </div>
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
import PrintableTeamScores from '../printables/PrintableTeamScores.vue'

export default {
  props: ['ballot', 'roundInfo'],
  components: {PrintableTeamScores},
  computed: {
    ballotsExcludingSelf: function() {
      var authorIndex = this.ballot.panel.indexOf(this.ballot.author);
      if (authorIndex > -1) {
        return this.ballot.panel.splice(authorIndex, 1);
      } else {
        return this.ballot.panel
      }
    }
  }
}
</script>
