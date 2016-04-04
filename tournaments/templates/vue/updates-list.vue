
<!-- Streaming Item Updates for TournamentOverview -->
<script type="text/x-template" id="updates-list">

  <li class='list-group-item'>
    <span class='badge'>[[ timestamp ]]</span>
    <strong>[[ user ]]</strong> [[ type ]] <em>[[ param ]]</em>
  </li>

</script>

<script>
  Vue.component('updates-list', {
    template: '#updates-list',
    props: {
      timestamp: String,
      user: String,
      type: String,
      param: String,
    },
  })
</script>
