<script>
// Subclass should set on root:
// draggable=true
// @dragstart="dragStart"
// @dragend="dragEnd"
// class="vue-draggable"
// :class="[componentClasses, isDragging ? vue-is-dragging : '']"
//
// Subclass can provide handleDragStart() and handleDragEnd()
// Subclasses should also provide a data payload
// Any :hover CSS rules on the subclass should instead be computed from isDragging
// else they wont be remove upon a drop

export default {
  data: function() { return { isDragging: false, isHovering: false }},
  props: { locked: false },
  computed: {
    draggableClasses: function() {
      var draggableCSS = "vue-draggable btn btn-sm "
      if (this.isHovering) {
        draggableCSS += "vue-is-hovering "
      }
      if (this.isDragging) {
        return draggableCSS += "vue-is-dragging "
      }
      if (this.locked) {
        return draggableCSS += "locked "
      }
      return draggableCSS
    },
  },
  methods: {
    dragStart: function(event) {
      if (this.locked) {
        event.preventDefault() // Firefox needs this
        return
      } else {
        this.isDragging = true;
        this.isHovering = true;
        // Set data on the drag event to uniquely record what is being dragged
        // Must have a setData handler here for Firefox to allow dragging;
        // see http://mereskin.github.io/dnd/
        event.dataTransfer.setData("text", this.draggablePayload);
        this.handleDragStart(event);
      }
    },
    dragEnd: function(event) {
      this.$nextTick(function () {
        this.isDragging = false;
        this.isHovering = false;
        this.handleDragEnd(event)
      })
    },
  }
}
</script>
