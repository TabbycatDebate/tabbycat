<template>

  <nav
    v-on:dragover.prevent
    v-on:dragenter="dragEnter"
    v-on:dragleave="dragLeave"
    v-on:drop="drop"
    v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
    class="navbar navbar-default navbar-fixed-bottom vue-droppable">

    <slot>
      <!-- Container sets unallocated items here -->
    </slot>

  </nav>

</template>

<script>
import DroppableMixin from '../mixins/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  props: {
  },
  computed: {
  },
  components: {
  },
  methods: {
  }
}
</script>