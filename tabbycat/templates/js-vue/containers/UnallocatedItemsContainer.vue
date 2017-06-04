<template>

  <nav
    v-on:dragover.prevent
    v-on:dragenter="dragEnter"
    v-on:dragleave="dragLeave"
    v-on:drop="drop"
    v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
    class="navbar navbar-default navbar-fixed-bottom vue-droppable unallocated-items">

    <slot><!-- Container sets unallocated items here --></slot>

  </nav>

</template>

<script>
import DroppableMixin from '../draganddrops/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin]
}
</script>