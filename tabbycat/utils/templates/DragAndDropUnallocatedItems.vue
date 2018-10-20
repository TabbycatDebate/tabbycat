<template>
  <div @dragover.prevent @dragenter="dragEnter" @dragleave="dragLeave" @drop="drop"
       class="n" :style="{height: 300 + 'px'}" ref="resizeableElement">

    <section class="resize-handler" @dragover.prevent @mousedown="resizeStart"
             data-toggle="tooltip">
      <i data-feather="menu" class="align-self-center mx-auto"></i>
    </section>

    <div :class="['vue-droppable', { 'vue-is-drag-enter': isDroppable }]">
      <div v-for="item in unallocatedItems" :is="unallocatedComponent"
           :item="item" :key="item.id"></div>
    </div>

  </div>
</template>

<script>
import DroppableMixin from '../../templates/draganddrops/DroppableMixin.vue'

export default {
  mixins: [DroppableMixin],
  props: ['unallocatedItems', 'unallocatedComponent'],
  methods: {
    handleDrop: function (event) {

    },
    resizeStart: function (event) {

    },
  },
}
</script>
