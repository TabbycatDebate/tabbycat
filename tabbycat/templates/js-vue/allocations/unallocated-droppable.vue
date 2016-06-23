<template>
  <adj-draggable v-for="adj in adjs" :adj="adj"></adj-draggable>
</template>

<script>
export default {
  props: {
    adjs: Array
  },
}
</script>