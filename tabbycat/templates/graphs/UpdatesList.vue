<template>

  <li class='list-group-item list-group-item-info'>
    <span class='badge'>
      {{ item.timestamp }}
    </span>
    <strong>{{ item.user }}</strong> {{ item.type }}
    <em>{{ item.param }}</em>
  </li>

</template>

<script>
export default {
  props: {
    item: Object,
  },
}
</script>
