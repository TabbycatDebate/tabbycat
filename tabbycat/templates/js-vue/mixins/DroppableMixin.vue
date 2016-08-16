<script>
// Subclass should set on root:
// v-on:dragover.prevent
// v-on:dragenter="dragEnter"
// v-on:dragleave="dragLeave"
// v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
// v-on:drop="drop"
// Subclasses can implement a handleDragEnter() handleDragLeave() handleDrop()

export default {
  props: {
    'isDroppable': { default: false },
    'dragCounter': { default: 0 },
  },
  methods: {
    dragEnter: function(event) {
      this.dragCounter++;
      this.isDroppable = true;
      if (typeof this.handleDragEnter === 'function') {
        this.handleDragEnter(event);
      }
    },
    dragLeave: function(event) {
      this.dragCounter--;
      if (this.dragCounter == 0) {
        this.isDroppable = false;
      }
      if (typeof this.handleDragLeave === 'function') {
        this.handleDragLeave(event);
      }
    },
    drop:  function(event) {
      this.dragCounter = 0;
      this.isDroppable = false;
      if (typeof this.handleDrop === 'function') {
        this.handleDrop(event);
      }
    },
  }
}
</script>
