<script>
// Subclass should set on root:
// @dragover.prevent
// @dragenter="dragEnter"
// @dragleave="dragLeave"
// :class="{ 'vue-droppable-enter': isDroppable }"
// @drop="drop"
// Subclasses can implement a handleDragEnter() handleDragLeave() handleDrop()

export default {
  data: function () { return { dragCounter: 0, isDroppable: false } },
  props: { locked: false },
  computed: {
    droppableClasses: function () {
      if (this.isDroppable && !this.locked) {
        return 'legacy-vue-droppable vue-droppable-enter'
      }
      if (this.locked) {
        return 'legacy-vue-droppable locked'
      }
      return 'legacy-vue-droppable'
    },
  },
  methods: {
    dragEnter: function (event) {
      this.dragCounter += 1
      this.isDroppable = true
      if (typeof this.handleDragEnter === 'function') {
        this.handleDragEnter(event)
      }
    },
    dragLeave: function (event) {
      this.dragCounter -= 1
      if (this.dragCounter === 0) {
        this.isDroppable = false
      }
      if (typeof this.handleDragLeave === 'function') {
        this.handleDragLeave(event)
      }
    },
    drop: function (event) {
      // Firefox needs to prevent original actions
      if (event.preventDefault) { event.preventDefault() }
      if (event.stopPropagation) { event.stopPropagation() }
      this.dragCounter = 0
      if (this.locked) {
        return
      }
      this.isDroppable = false
      if (typeof this.handleDrop === 'function') {
        const payloadData = event.dataTransfer.getData('text')
        this.handleDrop(JSON.parse(payloadData))
      }
    },
  },
}
</script>
