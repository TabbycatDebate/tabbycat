<template>

  <div class="btn-toolbar flex-nowrap">
    <div v-if="group.length > 0" v-for="group in groups" class="btn-group btn-group-sm mr-2">
      <button :class="['btn', item.css]" v-for="item in group">
        {{ item.title }}
      </button>
    </div>
  </div>

</template>

<script>

export default {
  mixins: [],
  props: { groups: Array },
}
</script>
