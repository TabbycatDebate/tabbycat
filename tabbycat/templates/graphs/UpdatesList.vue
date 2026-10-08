<script setup>
defineProps({
  item: Object,
})
</script>

<template>
  <li class="list-group-item text-info d-flex justify-content-between align-items-center">
    <div>
      <strong
        class="pr-1"
        v-html="item.user"
      />
      <span
        v-if="item.agent == 'a'"
        class="badge badge-light mr-1"
      >API</span>
      <span
        class="pr-1"
        v-html="item.type"
      />
      <em v-html="item.param" />
    </div>
    <span class="badge badge-light">{{ item.timestamp }}</span>
  </li>
</template>
