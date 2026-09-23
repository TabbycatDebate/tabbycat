<script setup>
import { createPopper } from '@popperjs/core'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { usePopoverManager } from '../composables/usePopoverManager.js'
// Inheriting components should provide a getPopOverTitle() method
// Along with providing an element with the "popover-raw" class as a direct
// descendent of the component's root template
// They can then trigger showPopover; ie "@mouseover="showPopover''
// Note that once triggered, it will handle its own show/hide events
//

defineProps({
  cellData: Object,
})

const { registerPopover, shouldHidePopover, activePopoverUid } = usePopoverManager()

const container = ref(null)
const popover = ref(null)

const showingPopOver = ref(false)
const hoveringPopOver = ref(false)
const popperInstance = ref(null)
const uid = ref(Math.floor(Math.random() * 1000000))

const setHoveringPopOver = (value) => {
  hoveringPopOver.value = value
}

const hidePopOver = (force = false) => {
  if (!hoveringPopOver.value || force) {
    showingPopOver.value = false
    hoveringPopOver.value = false
  }
}

const togglePopOver = (event) => {
  if (event && (event.pointerType === 'touch' || event.pointerType === 'pen')) {
    if (showingPopOver.value) {
      setTimeout(() => hidePopOver(), 150)
    } else {
      showingPopOver.value = true
    }
  }
}

const showPopOver = () => {
  registerPopover(uid.value)
  popperInstance.value?.setOptions?.({ placement: 'bottom' })
  showingPopOver.value = true
}

watch(activePopoverUid, () => {
  if (shouldHidePopover(uid.value)) {
    hidePopOver(true)
  }
})

onMounted(() => {
  popperInstance.value = createPopper(container.value, popover.value, {
    placement: 'right-end',
    strategy: 'fixed',
    modifiers: [
      {
        name: 'offset',
        options: {
          offset: [10, -20],
        },
      },
    ],
  })
})

onBeforeUnmount(() => {
  popperInstance.value?.destroy?.()
})
</script>

<template>
  <div
    ref="container"
    class="touch-target"
    @pointerup="togglePopOver"
  >
    <div
      class="hover-target"
      @mouseenter="showPopOver"
      @mouseleave="hidePopOver"
    >
      <slot>
        {{ cellData.content }}
      </slot>

      <div
        v-show="showingPopOver"
        ref="popover"
        class="popover bs-popover-bottom"
        role="tooltip"
        @mouseenter="setHoveringPopOver(true)"
        @mouseleave="setHoveringPopOver(false); hidePopOver()"
      >
        <div class="popover-header d-flex">
          <h6
            v-if="cellData.title"
            class="flex-grow-1"
            v-html="cellData.title"
          />
          <div
            class="popover-close"
            @click="hidePopOver(true)"
            @tap="hidePopOver(true)"
          >
            <i
              data-feather="x"
              class="hoverable text-danger"
            />
          </div>
        </div>
        <div class="popover-body">
          <div class="list-group list-group-item-flush">
            <div
              v-for="item in cellData.content"
              class="list-group-item"
            >
              <a
                v-if="item.link"
                :href="item.link"
                v-html="item.text"
              />
              <span
                v-else
                v-html="item.text"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
