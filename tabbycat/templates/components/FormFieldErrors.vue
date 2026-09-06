<script setup>
defineProps({
  errors: Array,
})
</script>

<template>
  <ul
    v-if="errors.length"
    class="errorlist"
  >
    <li
      v-for="error in errors"
      :key="error"
    >
      {{ error }}
    </li>
  </ul>
</template>
