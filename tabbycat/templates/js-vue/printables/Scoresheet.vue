<!-- Base Scoresheet Template -->
<template>

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="ballot.panel.length > 1">
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
        Your panellists are
        <span v-for="(i, adj) in ballotsExcludingSelf">
          <span v-if="i !== 0">&nbsp;and</span>&nbsp;<strong>{{ adj.name }}</strong>
          <span v-if="adj.position === 'c'">(Chair, {{ adj.institution }})</span>
          <span v-if="adj.position === 'o'">(Solo Chair, {{ adj.institution }})</span>
          <span v-if="adj.position === 'p'">(Panellist, {{ adj.institution }})</span>
          <span v-if="adj.position === 't'">(Trainee, {{ adj.institution }})</span>
        </span>
      </div>
    </div>
  </section>

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="data.hasMotions && !data.hasVetoes">
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
        Motion:
      </div>
      <div class="db-flex-item db-align-vertical-center">
        <em>{{ motions[0].text }}</em>
      </div>
    </div>
  </section>

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="data.hasMotions && data.hasVetoes">

    <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
      <div v-for="choice_type in ['Chosen Motion', 'Aff Veto', 'Neg Veto']" class="db-flex-item-1 db-flex-column">

        <div class="db-flex-item-2 db-align-horizontal-center db-align-vertical-end" v-html="choice_type"></div>
        <div class="db-flex-item-1 "></div>
        <div class="db-flex-item-2 db-flex-row">
          <div v-for="motion in motions" class="db-align-horizontal-center db-align-vertical-start db-flex-item-1 db-center-text">
            <span class="db-fill-in">{{ motion.seq }}</span>
          </div>
        </div>

      </div>
    </div>

    <div class="db-item-gutter"></div>
    <div class="db-flex-item-2 db-flex-row db-align-vertical-center">
      <template v-for="motion in motions" track-by="$index">
        {{ motion.seq }}: {{ motion.text }}<br>
      </template>
    </div>

  </section>

  <section class="db-flex-row db-flex-item-7 db-margins-m">
    <div class="db-flex-column db-bordered db-flex-item-half">
      <team-scores position="Aff" :speakers="ballot.affSpeakers" :name="ballot.aff" :emoji="ballot.affEmoji" :data="data"></team-scores>
    </div>
    <div class="db-item-gutter"></div>
    <div class="db-flex-column db-bordered db-flex-item-half">
      <team-scores position="Neg" :speakers="ballot.negSpeakers" :name="ballot.neg" :emoji="ballot.negEmoji" :data="data"></team-scores>
    </div>
  </section>

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1 db-flex-item-1" v-if="!isBP">
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

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1 db-flex-item-1" v-if="showInfo">
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row"><!-- Aff holder -->
      <div class="db-flex-item db-align-vertical-center db-flex-static db-vertical-center-text">
        {{ infoText }}
      </div>
    </div>
  </section>

</template>

<script>
import TeamScores from './TeamScores.vue'

export default {
  props: ['data', 'ballot', 'motions'],
  components: {
    TeamScores
  },
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
