<template>
  <div class="db-flex-column db-bordered db-flex-item-half">

    <div class="db-flex-item-3 db-flex-row db-bottom-border">
      <div class="db-padding-horizontal db-flex-item db-align-vertical-center">
        <div class="db-flex-item-1">
          <span class="h6">{{ team.short_name }}</span>
          <small>({{ speakersList }})</small>
        </div>
        <div class="db-flex-static">
          <h6>{{ titleCasePosition }}</h6>
        </div>
      </div>
      <div class="db-padding-horizontal db-flex-static "></div>
    </div>

    <div class="db-flex-item-2 db-flex-row db-bottom-border"><!-- Keys -->
      <div class="db-align-vertical-center db-left-text"
           :class="{ 'db-flex-item-fws': !roundInfo.isBP, 'db-flex-item-fwm': roundInfo.isBP }">
      </div>
      <div class="db-align-vertical-center db-padding-horizontal db-flex-item">
        <small>Speaker's First and Last Name</small>
      </div>
      <div v-if="roundInfo.showPronouns" class="db-align-vertical-center db-flex-item-fwxl">
        <small>Pronoun</small>
      </div>
      <div class="db-align-vertical-center db-padding-horizontal db-flex-item-fwxl">
        <small>Score</small>
      </div>
    </div>

    <div class="db-flex-item-3 db-flex-row db-bottom-border" v-for="x in roundInfo.speakersCount"><!-- Speakers -->
      <div class="db-align-vertical-center db-right-text"
           :class="{ 'db-flex-item-fws': !roundInfo.isBP, 'db-flex-item-fwm': roundInfo.isBP }">
        {{ getSpeakerName(x) }}
      </div>
      <div class="db-padding-horizontal db-fill-in db-flex-item"></div>
      <div v-if="roundInfo.showPronouns" class="db-padding-horizontal db-fill-in db-flex-item-fwxl"></div>
      <div class="db-padding-horizontal db-fill-in db-flex-item-fwxl"></div>
    </div>

    <div class="db-flex-item-3 db-flex-row db-bottom-border" v-if="roundInfo.hasReplies"><!-- Replies -->
      <div class="db-align-vertical-center db-right-text db-flex-item-fws">
        R
      </div>
      <div class="db-padding-horizontal db-fill-in db-flex-item"></div>
      <div v-if="roundInfo.showPronouns" class="db-padding-horizontal db-fill-in db-flex-item-fwxl"></div>
      <div class="db-padding-horizontal db-fill-in db-flex-item-fwxl"></div>
    </div>

    <div class="db-flex-item-3 db-flex-row"><!-- Totals -->
      <div class="db-align-vertical-center db-right-text"
           :class="{ 'db-flex-item-fws': !roundInfo.isBP, 'db-flex-item-fwm': roundInfo.isBP }">
        <span v-if="roundInfo.isBP">Rank</span>
      </div>
      <div class="db-padding-horizontal db-flex-item db-flex-row">
        <template v-if="roundInfo.isBP">
          <div class="db-flex-item-1  db-align-vertical-center db-align-horizontal-center">
            <span class="db-fill-in">1st</span>
          </div>
          <div class="db-flex-item-1  db-align-vertical-center db-align-horizontal-center">
            <span class="db-fill-in">2nd</span>
          </div>
          <div class="db-flex-item-1  db-align-vertical-center db-align-horizontal-center">
            <span class="db-fill-in">3rd</span>
          </div>
          <div class="db-flex-item-1  db-align-vertical-center db-align-horizontal-center">
            <span class="db-fill-in">4th</span>
          </div>
          <div class="db-flex-item-1"></div>
        </template>
      </div>
      <div class="db-padding-horizontal db-align-vertical-center db-flex-item-fwxl db-right-text">Total Score</div>
      <div class="db-padding-horizontal db-fill-in db-flex-item-fwxl"></div>
    </div>

  </div>
</template>

<script>
import _ from 'lodash'

export default {
  props: {
    dt: Object,
    roundInfo: Object
  },
  computed: {
    team: function() {
      if (this.dt.team === null) {
        console.log('null')
      } else {
        return this.dt.team
      }
    },
    speakersList: function() {
      var speakersList = ""
      _.forEach(this.dt.team.speakers, function(speaker) {
        speakersList += speaker.name + ", "
      })
      return speakersList.slice(0, -2);
    },
    titleCasePosition: function() {
      var upperWords = _.map(_.words(this.dt.position), function(word) {
        return _.upperFirst(word)
      })
      return _.join(upperWords, " ")
    }
  },
  methods: {
    getSpeakerName: function(order) {
      if (!this.roundInfo.isBP) {
        return order
      } else {
        if (this.dt.position === "opening government") {
          if (order === 1) { return "PM" } else { return "DPM" }
        } else if (this.dt.position === "opening opposition") {
          if (order === 1) { return "LO" } else { return "DLO" }
        } else if (this.dt.position === "closing government") {
          if (order === 1) { return "MG" } else { return "GW" }
        } else if (this.dt.position === "closing opposition") {
          if (order === 1) { return "MO" } else { return "OW" }
        }
      }
    }
  }
}
</script>
