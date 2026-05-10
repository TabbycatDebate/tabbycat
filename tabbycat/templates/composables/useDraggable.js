import { computed, ref } from 'vue'

export function useDraggable (props) {
  const isDragging = ref(false)
  const scrollStop = ref(false)
  const windowThresholds = 100

  const draggableClasses = computed(() => {
    let classes = 'vue-draggable '
    if (props.locked) {
      classes += ' vue-draggable-locked'
    } else if (isDragging.value) {
      classes += ' vue-draggable-dragging'
    }
    return classes
  })

  const scrollPage = (step) => {
    const $ = window.$ || window.jQuery
    if (!$) {
      return
    }
    const scrollY = $(window).scrollTop()
    $(window).scrollTop(scrollY + step)
  }

  const dragStart = (event) => {
    if (props.locked) {
      event.preventDefault()
    } else {
      isDragging.value = true
      event.dataTransfer.setData('text', JSON.stringify(props.dragPayload))
    }
    event.stopPropagation()
  }

  const dragEnd = (event) => {
    isDragging.value = false
    scrollStop.value = true
    event.stopPropagation()
  }

  const drag = (event) => {
    scrollStop.value = true
    if (event.clientY < windowThresholds) {
      scrollStop.value = false
      scrollPage(-1)
    }
    const windowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
    if (event.clientY > (windowHeight - windowThresholds)) {
      scrollStop.value = false
      scrollPage(1)
    }
  }

  return {
    isDragging,
    scrollStop,
    draggableClasses,
    dragStart,
    dragEnd,
    drag,
  }
}
