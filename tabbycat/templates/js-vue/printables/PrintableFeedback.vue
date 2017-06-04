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
    <feedback-question v-for="question in adjQuestions" :question="question" ></feedback-question>
  </template>

  <template v-if="ballot.authorPosition === 'Team'">
    <feedback-question v-for="question in teamQuestions" :question="question" ></feedback-question>
  </template>

</template>

<script>
import PrintableFeedbackQuestion from './PrintableFeedbackQuestion.vue'
import _ from 'lodash'

export default {
  components: {PrintableFeedbackQuestion},
  computed: {
    questionsOrderedBySeq: function() {
      return _.orderBy(this.data.questions, 'seq', ['asc'])
    },
    adjQuestions: function() {
      return _.filter(this.questionsOrderedBySeq, { 'from_adj':  'true' })
    },
    teamQuestions: function() {
      return _.filter(this.questionsOrderedBySeq, { 'from_team':  'true' })
    },
  },
  props: ['data', 'ballot'],
}
</script>
