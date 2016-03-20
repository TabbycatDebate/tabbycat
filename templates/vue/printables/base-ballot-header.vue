<!-- Base Ballot Header Template -->
<script type="text/x-template" id="base-ballot-header">

  <header class="db-margins-m db-flex-row db-flex-item-1">

    <div class="db-align-vertical-end db-flex-item-3">
      <h2>
        [[ data.tournamentName ]] [[ data.kind ]] from [[ ballot.author ]]
        <span v-if="ballot.authorPosition === 'C'">(Chair)</span>
        <span v-if="ballot.authorPosition === 'P'">(Panellist)</span>
        <span v-if="ballot.authorPosition === 'T'">(Trainee)</span>
        <span v-if="ballot.target">on [[ ballot.target ]]
          <span v-if="ballot.targetPosition === 'C'">(Chair)</span>
          <span v-if="ballot.targetPosition === 'P'">(Panellist)</span>
          <span v-if="ballot.targetPosition === 'T'">(Trainee)</span>
        </span>
      </h2>
    </div>
    <div class="db-flex-static db-align-vertical-end">
      <h2>[[ ballot.room ]] [[ data.round ]]</h2>
    </div>

  </header>

</script>

<!-- Division Droppable Component Behaviour -->
<script>
  Vue.component('base-ballot-header', {
    template: '#base-ballot-header',
    props: ['data', 'ballot'],
  })
</script>
