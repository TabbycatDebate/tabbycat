<template>

  <div class="btn-toolbar flex-nowrap">
    <template v-if="groups.length > 0">
      <div v-for="group in groups" class="btn-group btn-group-sm mr-2">
        <button :class="['btn', item.css]" v-for="item in group">
          {{ item.title }}
        </button>
      </div>
    </template>
  </div>

</template>

<script>

export default {
  mixins: [],
  props: { groups: Array },
}
</script>
