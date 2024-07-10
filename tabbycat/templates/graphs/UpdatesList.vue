<template>

  <li class='list-group-item text-info d-flex justify-content-between align-items-center'>
    <div>
      <strong v-html="item.user" class="pr-1"></strong>
      <span v-if="item.agent == 'a'" class="badge badge-light mr-1">API</span>
      <span v-html="item.type" class="pr-1"></span>
      <em v-html="item.param"></em>
    </div>
    <span class="badge badge-light">{{ item.timestamp }}</span>
  </li>

</template>

<script>
export default {
  props: {
    item: Object,
  },
}
</script>
