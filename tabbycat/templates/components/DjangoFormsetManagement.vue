<script setup>
defineProps({
  management: Object,
  totalForms: Number,
})
</script>

<template>
  <input
    :name="`${management.prefix}-TOTAL_FORMS`"
    type="hidden"
    :value="totalForms"
  >
  <input
    :name="`${management.prefix}-INITIAL_FORMS`"
    type="hidden"
    :value="management.initialForms"
  >
  <input
    :name="`${management.prefix}-MIN_NUM_FORMS`"
    type="hidden"
    :value="management.minNumForms"
  >
  <input
    :name="`${management.prefix}-MAX_NUM_FORMS`"
    type="hidden"
    :value="management.maxNumForms"
  >
</template>
