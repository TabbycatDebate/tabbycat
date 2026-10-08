<script setup>
import _ from 'lodash'
import { computed } from 'vue'
import { useFeatherIcon } from '../composables/useFeatherIcon.js'

const props = defineProps({ cellData: Object })

const tooltip = computed(() => {
  if (!_.isUndefined(props.cellData.tooltip)) {
    return 'tooltip'
  }
  return false
})

const icon = computed(() => {
  if (!_.isUndefined(props.cellData.icon)) {
    return props.cellData.icon
  }
  return false
})

const { getFeatherIcon } = useFeatherIcon(icon)
</script>

<template>
  <div class="flex-vertical-center">
    <!-- Icons or Emoji -->
    <i
      v-if="icon"
      :class="cellData.iconClass"
      v-html="getFeatherIcon"
    />
    <i
      v-if="cellData.emoji"
      class="emoji"
    >{{ cellData.emoji }}</i>

    <!-- Links and modals -->
    <div
      v-if="cellData.link || cellData.modal"
      :data-toggle="cellData.tooltip ? tooltip : ''"
      :title="cellData.tooltip"
    >
      <a
        v-if="cellData.link"
        :href="cellData.link"
      >
        <span
          class="tooltip-trigger"
          v-html="cellData.text"
        />
      </a>
      <a
        v-if="cellData.modal"
        :data-target="cellData.modal"
      >
        <span
          class="tooltip-trigger"
          v-html="cellData.text"
        />
      </a>
      <small
        v-if="cellData.subtext"
        v-html="cellData.subtext"
      />
    </div>

    <!-- Standard -->
    <div
      v-else
      :data-toggle="cellData.tooltip ? tooltip : ''"
      :title="cellData.tooltip"
    >
      <span
        class="tooltip-trigger"
        v-html="cellData.text"
      />
      <template v-if="cellData.subtext">
        <br><small v-html="cellData.subtext" />
      </template>
    </div>
  </div>
</template>
