<!-- Base Scoresheet Template -->
<template>

  <template v-if="ballot.authorPosition === 'Team'">
    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-padding-horizontal db-flex-static db-vertical-center-text">
          Did {{ ballot.target }} deliver the adjudication?
        </div>
        <div class="db-flex-item db-flex-row">
          <div class="db-align-horizontal-center db-padding-horizontal db-align-vertical-center db-flex-static db-center-text db-vertical-center-text">
            <span class="db-padding-horizontal db-fill-in">Yes</span>
          </div>
          <div class="db-align-horizontal-center db-padding-horizontal db-align-vertical-center db-flex-static db-center-text db-vertical-center-text">
            <span class="db-padding-horizontal ">No, I am submitting feedback on:</span>
          </div>
          <div class="db-align-horizontal-center db-fill-in db-align-vertical-center db-flex-item db-center-text db-vertical-center-text">
          </div>
        </div>
      </div>
    </section>
  </template>

  <template v-if="ballot.authorPosition !== 'Team'">
    <feedback-question v-for="question in data.questions | filterBy 'true' in 'from_adj' | orderBy 'seq'" :question="question" ></feedback-question>
  </template>

  <template v-if="ballot.authorPosition === 'Team'">
    <feedback-question v-for="question in data.questions | filterBy 'true' in 'from_team' | orderBy 'seq'" :question="question" ></feedback-question>
  </template>

</template>

<script>
  import FeedbackQuestion from './FeedbackQuestion.vue'
  export default {
    components: {
      FeedbackQuestion
    },
    props: ['data', 'ballot'],
  }
</script>
