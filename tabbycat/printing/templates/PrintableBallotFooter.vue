<template>
  <section class="db-margins-m db-bordered db-flex-row db-flex-item-fhs db-flex-static">

    <div :class="['db-padding-horizontal db-align-vertical-center  db-vertical-center-text',
                  showScoring ? 'db-flex-item-2' : 'db-flex-item-1']">
      <span>
        <span v-if="showScoring">
          Mark speeches
          {{ Math.round(roundInfo.substantiveMin) }} to {{ Math.round(roundInfo.substantiveMax) }};
          <strong>no ½ marks</strong>.</span>
        <span v-if="showScoring && roundInfo.hasReplies">
          Mark replies
          {{ Math.round(roundInfo.replyMin) }} to {{ Math.round(roundInfo.replyMax) }};
          <strong>½ marks are allowed</strong>.</span>
        <span v-if="returnLocation !== ''">Return ballots to {{ roundInfo.returnLocation }}.</span>
      </span>
    </div>

    <div class="db-item-gutter"></div>

    <div class="db-flex-item-1 db-flex-row">
      <div class="db-flex-item db-flex-static db-align-vertical-center db-right-text db-padding-horizontal">
        <em>Data Entry:</em>
      </div>
      <div class="db-flex-item db-fill-in ">
      </div>
      <div class="db-flex-item db-flex-static db-align-vertical-center db-right-text db-padding-horizontal">
        <em>Data Check:</em>
      </div>
      <div class="db-flex-item db-fill-in ">
      </div>
    </div>

  </section>
</template>

<script>
export default {
  props: ['roundInfo', 'showScoring']
}
</script>
