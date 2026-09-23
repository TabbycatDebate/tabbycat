<script setup>
import _ from 'lodash'
import { computed } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import PrintableFeedbackQuestion from './PrintableFeedbackQuestion.vue'

const props = defineProps({
  ballot: Object,
  roundInfo: Object,
})

const { gettext, tct } = useDjangoI18n()

const questionsOrderedBySeq = computed(() => {
  return _.orderBy(props.roundInfo.questions, 'seq', ['asc'])
})

const adjQuestions = computed(() => {
  return _.filter(questionsOrderedBySeq.value, ['from_adj', true])
})

const teamQuestions = computed(() => {
  return _.filter(questionsOrderedBySeq.value, ['from_team', true])
})
</script>

<template>
  <div class="db-flex-column db-flex-item-1">
    <section
      v-if="ballot.authorPosition === 'Team'"
      class="db-margins-m db-bordered db-flex-row db-flex-item-1"
    >
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-flex-static db-vertical-center-text">
          {{ tct('Did %s deliver the adjudication?', [ballot.target]) }}
        </div>
        <div class="db-flex-item db-flex-row">
          <div
            class="db-align-horizontal-center db-padding-horizontal db-align-vertical-center
                      db-flex-static db-center-text db-vertical-center-text"
          >
            <span class="db-padding-horizontal db-fill-in">{{ gettext('Yes') }}</span>
          </div>
          <div
            class="db-align-horizontal-center db-padding-horizontal db-align-vertical-center
                      db-flex-static db-center-text db-vertical-center-text"
          >
            <span class="db-padding-horizontal ">{{ gettext('No, I am submitting feedback on:') }}</span>
          </div>
          <div
            class="db-align-horizontal-center db-fill-in db-align-vertical-center
                      db-flex-item db-center-text db-vertical-center-text"
          />
        </div>
      </div>
    </section>

    <template v-if="ballot.authorPosition !== 'Team'">
      <printable-feedback-question
        v-for="question in adjQuestions"
        :key="question.text"
        :question="question"
      />
    </template>

    <template v-else>
      <printable-feedback-question
        v-for="question in teamQuestions"
        :key="question.text"
        :question="question"
      />
    </template>
  </div>
</template>
