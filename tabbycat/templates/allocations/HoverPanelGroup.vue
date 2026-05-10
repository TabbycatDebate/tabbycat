<script setup>
defineProps({ groups: Array })
</script>

<template>
  <div class="btn-toolbar flex-nowrap">
    <template v-if="groups !== null && groups.length > 0">
      <div
        v-for="group in groups"
        class="btn-group btn-group-sm mr-2"
      >
        <button
          v-for="item in group"
          :class="['btn', item.css]"
        >
          {{ item.title }}
        </button>
      </div>
    </template>
  </div>
</template>
