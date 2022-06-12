<script>

export default {
  props: {
    locked: {
      type: Boolean,
      default: false,
    },
    dragPayload: Object, // The context of the draggable item; sent to store
  },
  data: function () {
    return {
      isDragging: false,
      scrollStop: false,
      windowThresholds: 100, // Number of pixels to trigger scrolling
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
      this.scrollStop = true
    },
    drag: function (event) {
      // Setup the top and bottom of the windows as hover zones so we can scroll while dragging
      this.scrollStop = true
      if (event.clientY < this.windowThresholds) {
        this.scrollStop = false
        this.scrollPage(-1) // Faster close to top
      }
      const windowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
      if (event.clientY > (windowHeight - this.windowThresholds)) {
        this.scrollStop = false
        this.scrollPage(1)
      }
    },
    scrollPage: function (step) {
      var scrollY = $(window).scrollTop()
      $(window).scrollTop(scrollY + step)
    },
  },
}
</script>
