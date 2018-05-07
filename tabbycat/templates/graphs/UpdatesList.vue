<template>

  <li class='list-group-item text-info d-flex justify-content-between align-items-center'>
    <div>
      <strong v-html="item.user"></strong>
      <span v-html="item.type"></span>
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
