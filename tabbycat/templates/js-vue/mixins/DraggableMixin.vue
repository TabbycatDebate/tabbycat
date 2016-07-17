<script>
// Subclass should set on root:
// draggable=true
// v-on:dragstart="handleDragStart"
// v-on:dragend="handleDragEnd"
// class="vue-draggable"
// v-bind:class="[isDragging ? vue-is-dragging : '']"
// Subclass can provide handleDragStart() and handleDragEnd()
// Any :hover CSS rules on the subclass should instead be computed from isDragging
// else they wont be remove upon a drop

export default {
  props: {
    'isDragging': { default: false },
    'isHovering': { default: false },
  },
  start: 'parent-start',
  end: 'parent-end',
  methods: {
    dragStart: function(event) {
      this.isDragging = true;
      this.isHovering = true;
      this.$dispatch('dragging-team', this);
      if (typeof this.handledragEnd === 'function') {
        this.handledragEnd(event);
      }
    },
    dragEnd: function(event) {
      this.isDragging = false;
      this.isHovering = false;
      this.$dispatch('stopped-dragging');
      if (typeof this.handledragEnd === 'function') {
        this.handledragEnd(event);
      }
    },
  }
}
</script>
