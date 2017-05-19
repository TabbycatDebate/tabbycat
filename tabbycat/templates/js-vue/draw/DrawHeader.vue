<template>

  <div class="draw-header subtitle">

    <div class="thead flex-cell text-center" data-toggle="tooltip" title="Debate's Bracket">
      <span class="glyphicon glyphicon-stats"></span>
    </div>

    <div class="thead flex-cell text-center" data-toggle="tooltip" title="How many break categories are live in this room (across both teams)">
      <span class="glyphicon glyphicon-heart"></span>
    </div>

    <div class="thead flex-cell text-center" data-toggle="tooltip" title="The assigned importance value of this debate">
      <span class="glyphicon glyphicon-stats"></span>
    </div>

    <div class="thead flex-cell" data-toggle="tooltip" title="test">
      Venue
    </div>

    <div class="thead flex-cell debate-team" data-toggle="tooltip" title="test"
      v-for="position in positions">
      {{ position }}
    </div>

    <div class="thead flex-cell flex-6" data-toggle="tooltip" title="test">
      Panel
    </div>

  </div>

</template>

<script>

export default {
  components: {
  },
  mixins: [
  ],
  props: {
    positions: Array,
  },
  computed: {
  },
  methods: {
  },
  events: {
  }
}

</script>
