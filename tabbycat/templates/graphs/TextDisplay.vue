<template>
  <div class="row">

    <template v-for="(data, index) in set.data">

      <div class="col-4 text-center">
        <h5 :class="'mb-0 gender-text gender-' + data.label.toLowerCase()">
          {{ offset(data.count) }}
        </h5>
      </div>

      <div v-if="set.datum && index === 0" class="col-4 text-center">
        <h5 class="mb-0 text-body">
          {{ round(set.datum) }}
        </h5>
      </div>

    </template>

    <template v-if="set.data.length === 0">

      <div class="col-12 text-center text-muted">
        No Data Yet
      </div>

    </template>

    <div class="col text-center text-muted h6 mb-3 mt-2">
      {{ set.title }}
      <hr>
    </div>

  </div>
</template>

<script>
export default {
  props: {
    set: Object,
  },
  methods: {
    round: function (value) {
      return parseFloat(Math.round(value * 100) / 100).toFixed(2)
    },
    offset: function (value) {
      if (value > this.set.datum) {
        return `+${this.round(value - this.set.datum)}`
      } else if (value < this.set.datum) {
        return `-${this.round(this.set.datum - value)}`
      }
      return '=='
    },
  },
}
</script>
