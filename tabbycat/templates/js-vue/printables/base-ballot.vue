<!-- Base Ballot Template -->
<script type="text/x-template" id="base-ballot">

  <section class="db-score-sheet db-flex-item db-flex-column">

    <base-ballot-header :data="data" :ballot="ballot"></base-ballot-header>

    <base-scoresheet :data="data" :ballot="ballot" :motions="motions" v-if="data.kind === 'Scoresheet'"></base-scoresheet>

    <base-feedback :data="data" :ballot="ballot" v-if="data.kind === 'Feedback'"></base-feedback>

    <base-ballot-footer v-if="data.showTabRoomRow" :return-location="data.returnLocation"></base-ballot-footer>

  </section>

</script>

<!-- Division Droppable Component Behaviour -->
{% include "js-vue/printables/base-ballot-header.vue" %}
{% include "js-vue/printables/base-ballot-footer.vue" %}
{% include "js-vue/printables/base-scoresheet.vue" %}
{% include "js-vue/printables/base-feedback.vue" %}
<script>
  Vue.component('base-ballot', {
    template: '#base-ballot',
    props: ['data', 'ballot', 'motions'],
  })
</script>
