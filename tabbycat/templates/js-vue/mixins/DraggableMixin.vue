<script>
// Subclass should set on root:
// draggable=true
// v-on:dragstart="handleDragStart"
// v-on:dragend="handleDragEnd"
// class="vue-draggable"
// v-bind:class="[isDragging ? vue-is-dragging : '']"
// Subclass can provide handleDragStart() and handleDragEnd()

export default {
  props: {
    'isDragging': { default: false },
  },
  start: 'parent-start',
  end: 'parent-end',
  methods: {
    dragStart: function(event) {
      this.isDragging = true;
      this.$dispatch('dragging-team', this);
      if (typeof this.handledragEnd === 'function') {
        this.handledragEnd(event);
      }
    },
    dragEnd: function(event) {
      this.isDragging = false;
      this.$dispatch('stopped-dragging');
      if (typeof this.handledragEnd === 'function') {
        this.handledragEnd(event);
      }
    },
  }
}
</script>
