<script setup>
import { computed } from 'vue'
import { getIconNode } from '../icons.js'

const props = defineProps({
  name: String,
})

const icon = computed(() => getIconNode(props.name))
</script>

<template>
  <svg
    v-if="icon"
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="svg-icon"
    :data-icon="name"
    aria-hidden="true"
  >
    <component
      :is="tag"
      v-for="([tag, attrs], index) in icon"
      :key="index"
      v-bind="attrs"
    />
  </svg>
</template>
