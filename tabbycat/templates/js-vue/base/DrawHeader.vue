<template>

  <div class="row flex-horizontal subtitle">
    <div class="thead flex-cell text-center" data-toggle="tooltip" title="test">
      <span class="glyphicon glyphicon-stats"></span>
    </div>
    <div class="thead flex-cell text-center" data-toggle="tooltip" title="test">
      Venue
    </div>
    <div class="thead flex-cell debate-team" data-toggle="tooltip" title="test"
      v-for="position in positions">
      {{ position }}
    </div>
    <div class="thead flex-cell debate-team" data-toggle="tooltip" title="test">
      Neg
    </div>
    <div class="thead flex-cell flex-6 text-center" data-toggle="tooltip" title="test">
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
