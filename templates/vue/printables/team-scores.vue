<script type="text/x-template" id="team-scores">

  <div class="db-flex-item-2 db-flex-row db-bottom-border">
    <div class="db-padding-horizontal db-flex-item db-align-vertical-center db-flex-static">
      [[ position ]]
    </div>
    <div class="db-fill-in db-flex-item">
      [[ name ]]
    </div>
  </div>

  <div class="db-flex-item-2 db-flex-row db-bottom-border db-dont-fill-in"><!-- Keys -->
    <div class="db-align-vertical-center  db-left-text" v-bind:class="{ 'db-flex-item-fws': !data.isBP, 'db-flex-item-fwm': data.isBP }">
    </div>
    <div v-show="showPronouns" class="db-align-vertical-center db-align-horizontal-center db-flex-item-fwl">
      Pronoun
    </div>
    <div class="db-align-vertical-center db-padding-horizontal db-align-horizontal-center db-flex-item">
      Full Name
    </div>
    <div class="db-align-vertical-center db-flex-item-fwl db-align-horizontal-center">
      Score
    </div>
  </div>

  <div class="db-flex-item-2 db-flex-row" v-for="x in data.speakersCount"><!-- Speakers -->
    <div class="db-align-vertical-center db-right-text " v-bind:class="{ 'db-flex-item-fws': !isBP, 'db-flex-item-fwm': isBP }">
      [[ x + 1 ]]
    </div>
    <div v-show="showPronouns" class="db-fill-in db-flex-item-fwl">
    </div>
    <div class="db-padding-horizontal db-fill-in db-flex-item">
      [[ speakers[x] ]]
    </div>
    <div class="db-padding-horizontal db-fill-in db-flex-item-fwl">
    </div>
  </div>

  <div class="db-flex-item-2 db-flex-row db-bottom-border" v-show="hasReplies"><!-- Replies -->
    <div class="db-align-vertical-center db-right-text db-flex-item-fws">
      R.
    </div>
    <div class="db-padding-horizontal db-fill-in db-flex-item-fwl">
    </div>
    <div class="db-padding-horizontal db-fill-in db-flex-item">
    </div>
    <div class="db-fill-in db-flex-item-fwl">
    </div>
  </div>

  <div class="db-flex-item-2 db-flex-row"><!-- Totals -->
    <div class="db-align-vertical-center  db-left-text db-padding-horizontal" v-bind:class="{ 'db-flex-item-fws': !data.isBP, 'db-flex-item-fwm': data.isBP }">
    </div>
    <div class="db-flex-item db-flex-row db-align-vertical-center">
      <div class="db-align-vertical-center db-flex-item-1 db-left-text db-vertical-center-text" v-if="data.isBP">
        <span class="db-fill-in">
          1<sup>st</sup>
        </span>
      </div>
      <div class="db-align-vertical-center db-flex-item-1 db-left-text db-vertical-center-text" v-if="data.isBP">
        <span class="db-fill-in">
          2<sup>nd</sup>
        </span>
      </div>
      <div class="db-align-vertical-center db-flex-item-1 db-left-text db-vertical-center-text" v-if="data.isBP">
        <span class="db-fill-in">
          3<sup>rd</sup>
        </span>
      </div>
      <div class="db-align-vertical-center db-flex-item-1 db-left-text db-vertical-center-text" v-if="data.isBP">
        <span class="db-fill-in">
          4<sup>th</sup>
        </span>
      </div>
    </div>
    <div class="db-padding-horizontal db-static db-align-vertical-center db-right-text">
      Total Score:
    </div>
    <div class="db-fill-in db-flex-item-fwl">
    </div>
  </div>

</script>

<!-- Register Table Component Behaviour -->
<script>
  Vue.component('team-scores', {
    template: '#team-scores',
    props: {
      data: Object,
      name: String,
      speakers: Array,
      position: String,
    },
  })
</script>
