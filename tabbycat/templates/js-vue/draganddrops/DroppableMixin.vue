<script>
// Subclass should set on root:
// @dragover.prevent
// @dragenter="dragEnter"
// @dragleave="dragLeave"
// :class="{ 'vue-is-drag-enter': isDroppable }"
// @drop="drop"
// Subclasses can implement a handleDragEnter() handleDragLeave() handleDrop()

export default {
  data: function() { return { dragCounter: 0, isDroppable: false }},
  props: {  },
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
    drop: function(event) {
      this.dragCounter = 0;
      this.isDroppable = false;
      if (typeof this.handleDrop === 'function') {
        var payloadData = event.dataTransfer.getData("text");
        this.handleDrop(JSON.parse(payloadData));
      }
    },
  }
}
</script>
