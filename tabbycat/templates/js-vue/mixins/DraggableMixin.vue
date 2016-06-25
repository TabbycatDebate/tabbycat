<script>
// Subclass should set on root:
// draggable=true
// v-on:dragstart="handleDragStart"
// v-on:dragend="handleDragEnd"
// class="vue-draggable"
// v-bind:class="[isDragging ? vue-is-dragging : '']"

export default {
  props: {
    'isDragging': { default: false },
  },
  start: 'parent-start',
  end: 'parent-end',
  methods: {
    handleDragStart: function(elem) {
      console.log('handleDragStart', elem);
      this.isDragging = true;
      this.$dispatch('dragging-team', this);
    },
    handleDragEnd: function(elem) {
      this.isDragging = false;
      console.log('handleDragEnd', elem);
      this.$dispatch('stopped-dragging');
    },
  }
}
</script>
