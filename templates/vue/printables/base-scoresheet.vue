<!-- Base Scoresheet Template -->
<script type="text/x-template" id="base-scoresheet">

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="ballot.panel.length > 1">
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
        Your panellists are
        <span v-for="(index, adj) in ballot.panel">
          <template v-if="adj.name !== ballot.adjudicator">
            &nbsp;<span v-if="index !== 0">&nbsp;and</span>&nbsp;<strong>[[ adj.name ]]</strong>
            <span v-if="adj.position === 'C'">(Chair, [[ adj.institution]])</span>
            <span v-if="adj.position === 'P'">(Panellist, [[ adj.institution]])</span>
            <span v-if="adj.position === 'T'">(Trainee, [[ adj.institution]])</span>
          </template>
        </span>
      </div>
    </div>
  </section>

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="data.hasMotions and !data.hasVetoes">
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
        Motion:
      </div>
      <div class="db-flex-item db-align-vertical-center">
        <em>[[ motions[0].text ]]</em>
      </div>
    </div>
  </section>

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="data.hasMotions && data.hasVetoes">

    <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
      <div class="db-align-vertical-center db-flex-static">
        Chosen Motion:
      </div>
      <div class="db-flex-item-1 db-flex-row">
        <div v-for="(index, item) in motions" class="db-align-horizontal-center db-align-vertical-center db-align-horizontal-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">[[ index + 1 ]]</span>
        </div>
      </div>
      <div class="db-item-gutter"></div>
      <div class="db-align-vertical-center db-flex-static">
        Aff Veto:
      </div>
      <div class="db-flex-item-1 db-flex-row">
        <div v-for="(index, item) in motions" class="db-align-horizontal-center db-align-vertical-center db-align-horizontal-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">[[ index + 1 ]]</span>
        </div>
      </div>
      <div class="db-item-gutter"></div>
      <div class="db-align-vertical-center db-flex-static">
        Neg Veto:
      </div>
      <div class="db-flex-item-1 db-flex-row">
        <div v-for="(index, item) in motions" class="db-align-horizontal-center db-align-vertical-center db-align-horizontal-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">[[ index + 1 ]]</span>
        </div>
      </div>
    </div>
    <div class="db-item-gutter"></div>
    <div class="db-flex-item-1 db-flex-row db-align-vertical-center">
      <template v-for="(index, item) in motions">
        [[ index + 1]]: [[ item.text ]]<br>
      </template>
    </div>

  </section>

  <section class="db-flex-row db-flex-item-7 db-margins-m">
    <div class="db-flex-column db-bordered db-flex-item-half">
      <team-scores position="Affirmative" :speakers="ballot.affSpeakers" :name="ballot.aff" :emoji="ballot.affEmoji" :data="data"></team-scores>
    </div>
    <div class="db-item-gutter"></div>
    <div class="db-flex-column db-bordered db-flex-item-half">
      <team-scores position="Negative" :speakers="ballot.negSpeakers" :name="ballot.neg" :emoji="ballot.negEmoji" :data="data"></team-scores>
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
        [[ infoText ]]
      </div>
    </div>
  </section>

</script>

{% include "vue/printables/team-scores.vue" %}
<script>
  Vue.component('base-scoresheet', {
    template: '#base-scoresheet',
    props: ['data', 'ballot', 'motions'],

  })
</script>
