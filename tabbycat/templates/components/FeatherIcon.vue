<script setup>
import { toRef } from 'vue'
import { useFeatherIcon } from '../composables/useFeatherIcon.js'

const props = defineProps({
  name: String,
})

const { getFeatherIcon } = useFeatherIcon(toRef(props, 'name'))
</script>

<template>
  <span v-html="getFeatherIcon" />
</template>
