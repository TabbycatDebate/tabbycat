<script>
// Subclass should set on root:
// v-on:dragover.prevent
// v-on:dragenter="handleDragEnter"
// v-on:dragleave="handleDragLeave"
// v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
// v-on:drop="handleDrop"
// Should then implement a receiveDrop() function

export default {
  props: {
    'isDroppable': { default: false },
    'dragCounter': { default: 0 },
  },
  methods: {
    handleDragEnter: function(elem) {
      this.dragCounter++;
      // console.log('handleDragStart', elem);
      this.isDroppable = true;
    },
    handleDragLeave: function(elem) {
      this.dragCounter--;
      // console.log('handleDragEnd', elem);
      if (this.dragCounter == 0) {
        this.isDroppable = false;
      }
    },
    handleDrop:  function(event) {
      // console.log('handleDrop', elem);
      this.isDroppable = false;
      this.dragCounter = 0;
      this.receiveDrop(event);
    },
  }
}
</script>
