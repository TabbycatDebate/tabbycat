<template>

  <div @dragover.prevent  @drop="drop" :class="droppableClasses"
       @dragenter="dragEnter" @dragleave="dragLeave" @dragend="dragEnd">

    <slot></slot>

  </div>

</template>

<script>
import DroppableMixin from './DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
}
</script>
