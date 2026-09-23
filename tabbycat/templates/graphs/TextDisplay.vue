<script setup>
const props = defineProps({
  set: Object,
})

const round = (value) => {
  return parseFloat(Math.round(value * 100) / 100).toFixed(2)
}

const offset = (value) => {
  if (value > props.set.datum) {
    return `+${round(value - props.set.datum)}`
  } else if (value < props.set.datum) {
    return `-${round(props.set.datum - value)}`
  }
  return '=='
}
</script>

<template>
  <div class="row">
    <template v-for="(data, index) in set.data">
      <div class="col-4 text-center">
        <h5 :class="'mb-0 gender-text gender-' + data.label.toLowerCase()">
          {{ offset(data.count) }}
        </h5>
      </div>

      <div
        v-if="set.datum && index === 0"
        class="col-4 text-center"
      >
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
