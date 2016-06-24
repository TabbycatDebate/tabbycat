<template>

  <adjudicator-draggable
    v-for="adj in adjudicators"
    :adj="adj">
  </adjudicator-draggable>

</template>

<script>
import AdjudicatorDraggable from './AdjudicatorDraggable.vue'

export default {
  props: {
    adjudicators: Array
  },
  components: {
    'AdjudicatorDraggable': AdjudicatorDraggable
  }
}
</script>