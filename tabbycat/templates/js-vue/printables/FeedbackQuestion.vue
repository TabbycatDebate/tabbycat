<template>

  <template v-if="question.type === 'bs' || question.type === 'bc'">
    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-padding-horizontal db-flex-item db-flex-static db-vertical-center-text">
          {{ question.text }}
        </div>
        <div class="db-flex-item db-flex-row">
          <div class="db-align-horizontal-center db-align-vertical-center db-flex-item db-center-text db-vertical-center-text">
            <span class="db-fill-in">Yes</span>
          </div>
          <div v-if="question.type === 'bc'" class="db-align-horizontal-center db-align-vertical-center db-flex-item db-center-text db-vertical-center-text">
            <span class="db-fill-in">Unsure</span>
          </div>
          <div class="db-align-horizontal-center db-align-vertical-center db-flex-item db-center-text db-vertical-center-text">
            <span class="db-fill-in">No</span>
          </div>
        </div>
      </div>
    </section>
  </template>

  <template v-if="question.type === 'ss' || question.type === 'ms'">
    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-padding-horizontal db-flex-item db-flex-static db-vertical-center-text">
          {{ question.text }}</span>:
        </div>
        <div class="db-flex-item db-flex-row">
          <div v-for="choice in question.choice_options" class="db-align-horizontal-center db-align-vertical-center db-flex-item db-center-text db-vertical-center-text">
            <span class="db-fill-in">{{ choice }}</span>
          </div>
        </div>
      </div>
    </section>
  </template>

  <template v-if="question.type === 'is' || question.type === 'i' || question.type === 'f'">
    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-padding-horizontal db-flex-item db-flex-static db-vertical-center-text">
          {{ question.text }}</span>:
        </div>
        <div class="db-flex-item db-flex-row">
          <div v-for="choice in question.choice_options" class="db-align-horizontal-center db-align-vertical-center db-flex-item db-center-text db-vertical-center-text">
            <span class="db-fill-in">{{ choice }}</span>
          </div>
        </div>
      </div>
    </section>
  </template>

  <template v-if="question.type === 't'">
    <section class="db-margins-m db-bordered db-flex-row db-flex-item-1">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-row">
        <div class="db-align-vertical-center db-padding-horizontal db-flex-item db-flex-static db-vertical-center-text">
          {{ question.text }}
        </div>
        <div class="db-flex-item db-fill-in">
        </div>
      </div>
    </section>
  </template>

  <template v-if="question.type === 'tl'">
    <section class="db-margins-m db-bordered db-flex-row db-flex-item-20">
      <div class="db-padding-horizontal db-flex-item-1 db-flex-column">
        <div class="db-padding-horizontal db-flex-item db-flex-item-fhm db-align-vertical-center">
          {{ question.text }}
        </div>
        <div class="db-padding-horizontal db-flex-item db-ruled-bg"></div>
      </div>
    </section>
  </template>

</template>

<script>
export default {
  props: ['question'],
}
</script>
