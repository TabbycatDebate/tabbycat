<!-- Base Scoresheet Template -->
<script type="text/x-template" id="base-feedback">

  <template v-for="question in data.questions | orderBy 'seq'">
    <feedback-question :question="question" ></feedback-question>
  </template>

</script>

{% include "vue/printables/feedback-question.vue" %}
<script>
  Vue.component('base-feedback', {
    template: '#base-feedback',
    props: ['data', 'ballot'],
  })
</script>
