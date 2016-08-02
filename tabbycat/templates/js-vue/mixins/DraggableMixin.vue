<script>
// Subclass should set on root:
// draggable=true
// v-on:dragstart="dragStart"
// v-on:dragend="dragEnd"
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
      // For dragging to work in FF we need to do some kind of setData
      event.dataTransfer.setData('ID', this.id);
      if (typeof this.handleDragStart === 'function') {
        this.handleDragStart(event);
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
