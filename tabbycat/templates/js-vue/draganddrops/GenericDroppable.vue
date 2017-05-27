<template>

  <div>

    <slot>
      <!-- Container sets dropped items here -->
    </slot>

  </div>

</template>

<script>
import DraggableMixin from '../mixins/DraggableMixin.vue'
import AjaxMixin from '../mixins/AjaxMixin.vue'

export default {
  mixins: [DraggableMixin, AjaxMixin],
  props: {
    droppable: Object,
  },
  methods: {
    handleDragStart: function(event) {
    },
    handleDragEnd: function(event) {
    },
  }
}
</script>
