<template>

  <div @dragover.prevent @dragenter="dragEnter" @dragleave="dragLeave" @drop="drop"
       :class="droppableClasses">

    <slot></slot>

  </div>

</template>

<script>
import DroppableMixin from './DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
}
</script>
