<!-- Base Scoresheet Template -->
<script type="text/x-template" id="base-scoresheet">

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1">
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
        Your Name:
      </div>
      <div class="db-flex-item db-fill-in">

      </div>
    </div>
    <div class="db-item-gutter"></div>
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row" v-if="!isBP">
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text ">
        You Are:
      </div>
      <div class="db-flex-item db-flex-row">
        <div class="db-align-horizontal-center db-align-vertical-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">The Chair</span>
        </div>
        <div class="db-align-horizontal-center db-align-vertical-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">A Panellist</span>
        </div>
        <div class="db-align-horizontal-center db-align-vertical-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">A Trainee</span>
        </div>
      </div>
    </div>
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row" v-if="isBP">
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
        Your Panellists:
      </div>
      <div class="db-flex-item db-fill-in">
      </div>
    </div>
  </section>

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1" v-if="hasMotionSelection">
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text">
        The Motion:
      </div>
      <div class="db-flex-item db-fill-in">
      </div>
    </div>
    <div class="db-item-gutter"></div>
    <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text ">
        Aff Veto:
      </div>
      <div class="db-flex-item db-flex-row">
        <div class="db-align-horizontal-center db-align-vertical-center db-align-horizontal-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">1</span>
        </div>
        <div class="db-align-horizontal-center db-align-vertical-center db-align-horizontal-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">2</span>
        </div>
        <div class="db-align-horizontal-center db-align-vertical-center db-align-horizontal-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">3</span>
        </div>
      </div>
      <div class="db-item-gutter"></div>
      <div class="db-align-vertical-center db-flex-item db-flex-static db-vertical-center-text ">
        Neg Veto:
      </div>
      <div class="db-flex-item db-flex-row">
        <div class="db-align-horizontal-center db-align-vertical-center db-align-horizontal-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">1</span>
        </div>
        <div class="db-align-horizontal-center db-align-vertical-center db-align-horizontal-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">2</span>
        </div>
        <div class="db-align-horizontal-center db-align-vertical-center db-align-horizontal-center db-flex-item-1 db-center-text db-vertical-center-text">
          <span class="db-fill-in">3</span>
        </div>
      </div>
    </div>
  </section>

  <section class="db-flex-row db-flex-item-7 db-margins-m">
    <div class="db-flex-column db-bordered db-flex-item-half">
      <team-scores position="Affirmative" :speakers="ballot.affSpeakers" :name="ballot.aff" :data="data"></team-scores>
    </div>
    <div class="db-item-gutter"></div>
    <div class="db-flex-column db-bordered db-flex-item-half">
      <team-scores position="Negative" :speakers="ballot.negSpeakers" :name="ballot.neg" :data="data"></team-scores>
    </div>
  </section>

  <section class="db-flex-row db-flex-item-7 db-margins-m " v-if="isBP">
    <div class="db-flex-column db-bordered db-flex-item-half">
      <team-scores :n=2 :double-up=doubleUp :page-orientation=pageOrientation :is-bp=isBP :show-pronouns=showPronouns :has-replies=hasReplies :speakers-count=speakersCount></team-scores>
    </div>
    <div class="db-item-gutter"></div>
    <div class="db-flex-column db-bordered db-flex-item-half">
      <team-scores :n=3 :double-up=doubleUp :page-orientation=pageOrientation :is-bp=isBP :show-pronouns=showPronouns :has-replies=hasReplies :speakers-count=speakersCount></team-scores>
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
    props: ['data', 'ballot'],

  })
</script>
