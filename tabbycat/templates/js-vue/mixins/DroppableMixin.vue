<script>
// Subclass should set on root:
// v-on:dragover.prevent
// v-on:dragenter="handleDragEnter"
// v-on:dragleave="handleDragLeave"
// v-bind:class="{ 'vue-is-drag-enter': isDroppable }"

// Custom hooks:
// v-on:drop="customFunction"

export default {
  props: {
    'isDroppable': { default: false },
    'dragCounter': { default: 0 },
  },
  methods: {
    handleDragEnter: function(elem) {
      this.dragCounter++;
      console.log('handleDragStart', elem);
    },
    handleDragLeave: function(elem) {
      this.dragCounter--;
      console.log('handleDragEnd', elem);
      if (this.dragCounter == 0) {
        this.isDroppable = false;
      }
    },
  }
}
</script>
