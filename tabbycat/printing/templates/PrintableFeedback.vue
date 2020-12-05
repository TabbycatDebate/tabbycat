<template>
  <div class="db-flex-column db-flex-item-1">

    <section v-if="ballot.authorPosition === 'Team'"
             class="db-margins-m db-bordered db-flex-row db-flex-item-1">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-flex-static db-vertical-center-text"
             v-text="tct('Did %s deliver the adjudication?', [ballot.target])"></div>
        <div class="db-flex-item db-flex-row">
          <div class="db-align-horizontal-center db-padding-horizontal db-align-vertical-center
                      db-flex-static db-center-text db-vertical-center-text">
            <span class="db-padding-horizontal db-fill-in" v-text="gettext('Yes')"></span>
          </div>
          <div class="db-align-horizontal-center db-padding-horizontal db-align-vertical-center
                      db-flex-static db-center-text db-vertical-center-text">
            <span class="db-padding-horizontal " v-text="gettext('No, I am submitting feedback on:')"></span>
          </div>
          <div class="db-align-horizontal-center db-fill-in db-align-vertical-center
                      db-flex-item db-center-text db-vertical-center-text">
          </div>
        </div>
      </div>
    </section>

    <template v-if="ballot.authorPosition !== 'Team'">
      <printable-feedback-question v-for="question in adjQuestions" :question="question"
        :key="question.text" ></printable-feedback-question>
    </template>

    <template v-else>
      <printable-feedback-question v-for="question in teamQuestions"
        :question="question" :key="question.text" ></printable-feedback-question>
    </template>

  </div>
</template>

<script>
import _ from 'lodash'
import PrintableFeedbackQuestion from './PrintableFeedbackQuestion.vue'

export default {
  components: { PrintableFeedbackQuestion },
  computed: {
    questionsOrderedBySeq: function () {
      return _.orderBy(this.roundInfo.questions, 'seq', ['asc'])
    },
    adjQuestions: function () {
      return _.filter(this.questionsOrderedBySeq, ['from_adj', true])
    },
    teamQuestions: function () {
      return _.filter(this.questionsOrderedBySeq, ['from_team', true])
    },
  },
  props: ['ballot', 'roundInfo'],
}
</script>
