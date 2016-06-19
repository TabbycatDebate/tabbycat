<!-- Streaming Item Updates for TournamentOverview -->
<template>

  <li class='list-group-item'>
    <span class='badge'>
      {{ timestamp }}
    </span>
    <strong>{{ user }}</strong> {{ type }} <em>{{ param }}</em>
  </li>

</template>

<script>
export default {
  props: {
    timestamp: String,
    user: String,
    type: String,
    param: String,
  },
}
</script>
