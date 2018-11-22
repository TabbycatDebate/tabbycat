<script>

export default {
  props: {
    locked: false,
    dragPayload: Object, // The context of the draggable item; sent to store
  },
  data: function () {
    return {
      isDragging: false,
    }
  },
  computed: {
    dragableClasses: function () {
      let classes = 'vue-draggable '
      if (this.locked) {
        classes += ' vue-draggable-locked'
      } else if (this.isDragging) {
        classes += ' vue-draggable-dragging'
      }
      return classes
    },
  },
  methods: {
    dragStart: function (event) {
      if (this.locked) {
        event.preventDefault() // Firefox needs this
      } else {
        this.isDragging = true
        // Set data on the drag event to uniquely record what is being dragged
        // Must have a setData handler here for Firefox to allow dragging;
        // see http://mereskin.github.io/dnd/
        // Must also be a string; so we serialise to JSON
        event.dataTransfer.setData('text', JSON.stringify(this.dragPayload))
      }
    },
    dragEnd: function (event) {
      this.isDragging = false
    },
  },
}
</script>
