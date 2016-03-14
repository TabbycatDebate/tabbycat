<!-- Base Ballot Template -->
<script type="text/x-template" id="base-ballot">

  <section class="db-score-sheet db-flex-item db-flex-column">

    <base-ballot-header :kind="kind" :tournament-name="data.tournamentName" :room="ballot.room" :round="round"></base-ballot-header>

    <base-scoresheet :data="data" :ballot="ballot"></base-scoresheet>

    <base-ballot-footer v-if="data.showTabRoomRow" :return-location="data.returnLocation"></base-ballot-footer>

  </section>

</script>

<!-- Division Droppable Component Behaviour -->
<script>
  Vue.component('base-ballot', {
    template: '#base-ballot',
    props: ['round', 'data', 'ballot', 'kind'],
  })
</script>
