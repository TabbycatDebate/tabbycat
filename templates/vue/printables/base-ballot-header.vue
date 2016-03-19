<!-- Base Ballot Header Template -->
<script type="text/x-template" id="base-ballot-header">

  <header class="db-margins-m db-flex-row db-flex-item-1">

    <div class="db-align-vertical-end db-flex-item-3">
      <h2>
        [[ data.tournamentName ]] [[ data.kind ]] for [[ ballot.adjudicator ]]
        <span v-if="ballot.position === 'C'">(Chair, [[ ballot.adjudicatorInstitution ]])</span>
        <span v-if="ballot.position === 'P'">(Panellist, [[ ballot.adjudicatorInstitution ]])</span>
        <span v-if="ballot.position === 'T'">(Trainee, [[ ballot.adjudicatorInstitution ]])</span>
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
