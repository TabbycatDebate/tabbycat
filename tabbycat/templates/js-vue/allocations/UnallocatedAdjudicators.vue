<template>
  <adjudicator-draggable v-for="adj in adjs" :adj="adj"></adjudicator-draggable>
</template>

<script>
import AdjudicatorDraggable from './AdjudicatorDraggable.vue'

export default {
  props: {
    adjs: Array
  },
  components: {
    'AdjudicatorDraggable': AdjudicatorDraggable
  }
}
</script>