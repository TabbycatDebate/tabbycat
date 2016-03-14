<!-- Base Ballot Header Template -->
<script type="text/x-template" id="base-ballot-header">

  <header class="db-margins-m db-flex-row db-flex-item-1">

    <div class="db-align-vertical-end db-flex-item-1">
      <h2>
        [[ tournamentName ]] [[ kind ]]
      </h2>
    </div>

    <div class="db-item-gutter"></div>

    <div class="db-flex-item-1 db-flex-row db-padding-horizontal db-flex-row ">
      <div class="db-align-vertical-end db-flex-item db-vertical-center-text">
        <h2></h2>
      </div>
      <div class="db-align-vertical-end db-flex-item db-vertical-center-text">
        <h2>[[ room ]]</h2>
      </div>
      <div class="db-align-vertical-end db-flex-item db-vertical-center-text">
        <h2>[[ round ]]</h2>
      </div>
    </div>

  </header>

</script>

<!-- Division Droppable Component Behaviour -->
<script>
  Vue.component('base-ballot-header', {
    template: '#base-ballot-header',
    props: ['kind', 'tournamentName', 'room', 'round']
  })
</script>
