<template>
  <div class="row">

    <template v-for="(data, index) in set.data">

      <div class="col-md-4 text-center">
        <h4 :class="'no-bottom-margin text-body gender-text gender-' + data.label.toLowerCase()">
          {{ offset(data.count) }}
        </h4>
      </div>

      <div v-if="set.datum && index == 0" class="col-md-4 text-center">
        <h4 class="no-bottom-margin text-body">
          {{ round(set.datum) }}
        </h4>
      </div>

    </template>

    <div class="row">
     <h5 class="text-center mb-3">{{ set.title }}</h5>
    </div>

  </div>
</template>

<script>
export default {
  props: {
    set: Object,
  },
  methods: {
    round: function(value) {
      return parseFloat(Math.round(value * 100) / 100).toFixed(2);
    },
    offset: function(value) {
      var off = this.set.datum - value
      if (off > 0) {
        return "+" + this.round(off)
      } else {
        return this.round(off)
      }
    }
  }
}
</script>
