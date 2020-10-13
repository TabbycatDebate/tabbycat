<template>

  <v-touch class="touch-target" ref="container" v-on:tap="togglePopOver">
    <div class="hover-target" @mouseenter="showPopOver" @mouseleave="hidePopOver">

      <slot>
        {{ cellData.content }}
      </slot>

      <div class="popover bs-popover-bottom" role="tooltip" ref="popover"
           v-show="showingPopOver" @mouseenter="hoveringPopOver = true" @mouseleave="hidePopOver">
        <div class="popover-header d-flex">
          <h6 class="flex-grow-1" v-if="cellData.title">{{ cellData.title }}</h6>
          <div class="popover-close" v-on:click="hidePopOver(true)" v-on:tap="hidePopOver(true)">
            <i data-feather="x" class="hoverable text-danger"></i>
          </div>
        </div>
        <div class="popover-body">
          <div class="list-group list-group-item-flush">
            <div class="list-group-item" v-for="item in cellData.content">
              <a :href="item.link" v-if="item.link" v-html="item.text"></a>
              <span v-else v-html="item.text"></span>
            </div>
          </div>
        </div>
      </div>

    </div>

  </v-touch>

</template>

<script>
import { createPopper } from '@popperjs/core'
// Inheriting componets should provide a getPopOverTitle() method
// Along with providing an element with the "popover-raw" class as a direct
// descendent of the component's root template
// They can then trigger showPopover; ie "@mouseover="showPopover''
// Note that once triggered, it will handle its own show/hide events

export default {
  props: {
    cellData: Object,
  },
  data: function () {
    return {
      showingPopOver: false,
      hoveringPopOver: false, // If mouse is hovering inside the popover
      popperInstance: Object,
    }
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('hideOtherPopOvers', this.responeToGlobalHide)
  },
  mounted: function () {
    this.popperInstance = createPopper(this.$refs.container.$el, this.$refs.popover, {
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
  },
  methods: {
    togglePopOver: function (event) {
      if (event.pointerType === 'touch') { // Don't response to clicks as taps
        if (this.showingPopOver) {
          // Need to give time to taps on links to register
          setTimeout(() => this.hidePopOver(), 150)
        } else {
          this.showingPopOver = true
        }
      }
    },
    showPopOver: function () {
      this.$eventHub.$emit('hideOtherPopOvers', self._uid)
      this.popperInstance.setOptions({ placement: 'bottom' })
      this.showingPopOver = true
    },
    hidePopOver: function (force = false) {
      if (!this.hoveringPopOver || force) {
        // To access link items in the popover the cursor will leave the main element
        // So don't dismiss the popover if this is the case
        this.showingPopOver = false
        this.hoveringPopOver = false
      }
    },
    responeToGlobalHide (uid) {
      if (this._uid !== uid) {
        this.hidePopOver(true)
      }
    },
  },
}
</script>
