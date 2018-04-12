<template>
  <section class="db-margins-m db-bordered db-flex-row db-flex-item-fhs db-flex-static">

    <div :class="['db-padding-horizontal db-align-vertical-center  db-vertical-center-text',
                  showScoring ? 'db-flex-item-2' : 'db-flex-item-1']">
      <span>
        <span v-if="showScoring">
          Mark speeches
          {{ getDisplayNumber(roundInfo.substantiveMin) }} to {{ getDisplayNumber(roundInfo.substantiveMax) }};
          <strong>{{ getDisplayStep(roundInfo.substantiveStep) }}</strong>.</span>
        <span v-if="showScoring && roundInfo.hasReplies">
          Mark replies
          {{ getDisplayNumber(roundInfo.replyMin) }} to {{ getDisplayNumber(roundInfo.replyMax) }};
          <strong>{{ getDisplayStep(roundInfo.replyStep) }}</strong>.</span>
        <span v-if="returnLocation !== ''">Return ballots to {{ roundInfo.returnLocation }}.</span>
      </span>
    </div>

    <div class="db-item-gutter"></div>

    <div class="db-flex-item-1 db-flex-row">
      <div class="db-flex-item db-flex-static db-align-vertical-center db-right-text db-padding-horizontal">
        <em>Data Entry</em>
      </div>
      <div class="db-flex-item db-fill-in ">
      </div>
      <div class="db-flex-item db-flex-static db-align-vertical-center db-right-text db-padding-horizontal">
        <em>Data Check</em>
      </div>
      <div class="db-flex-item db-fill-in ">
      </div>
    </div>

  </section>
</template>

<script>
export default {
  props: ['roundInfo', 'showScoring'],
  methods: {
    getDisplayNumber: function (number) {
      if (number % 1 === 0) {
        return Math.round(number)
      } else {
        return number
      }
    },
    getDisplayStep: function (number) {
      if (number % 1 === 0) {
        return "no ½ marks"
      } else if (number % 0.5 === 0) {
        return "½ marks are allowed"
      } else {
        return "decimal marks are allowed"
      }
    }
  }
}
</script>
