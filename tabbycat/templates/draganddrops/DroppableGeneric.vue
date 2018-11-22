<template>
  <div :class="[droppableClasses, extraCss]"
       @dragover.prevent @drop="drop"
       @dragenter="dragEnter" @dragleave="dragLeave">

    <div v-if="locked" class="legacy-vue-droppable-lock-spinner">
      <i class="spinning" v-html="getFeatherIcon"></i>
    </div>
    <slot><!-- Container sets the dropped items here --></slot>

  </div>
</template>

<script>
import LegacyDroppableMixin from '../draganddrops/LegacyDroppableMixin.vue'
import FeatherMixin from '../tables/FeatherMixin.vue'

export default {
  mixins: [LegacyDroppableMixin, FeatherMixin],
  props: { assignmentId: Number, assignmentPosition: String, extraCss: '' },
  data: function () {
    return { icon: 'loader' }
  },
  methods: {
    handleDrop: function (event) {
      this.$eventHub.$emit('assign-draggable', event, this.assignmentId, this.assignmentPosition)
    },
  },
}
</script>
