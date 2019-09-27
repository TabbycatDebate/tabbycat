<template>
  <draggable-item :drag-payload="dragPayload" :class="{ 'bg-dark text-white': !item.available }">

      <span slot="number">
        <small class="pl-2 vue-draggable-muted ">{{ item.priority }}</small>
      </span>
      <span slot="title">
        {{ item.display_name }}
      </span>
      <span slot="subtitle">

      </span>

  </draggable-item>
</template>

<script>
import DraggableItem from '../../utils/templates/DraggableItem.vue'

export default {
  components: { DraggableItem },
  props: { item: Object, dragPayload: Object, isTrainee: false },
  computed: {

  },
}
</script>
