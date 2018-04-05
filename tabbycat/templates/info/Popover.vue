<template>

  <v-touch class="touch-target" ref="container" v-on:tap="togglePopOver">
    <div class="hover-target" @mouseenter="showPopOver">

        <slot>
          {{ content }}
        </slot>

    </div>
  </v-touch>

</template>

<script>
import _ from 'lodash'
// Inheriting componets should provide a getPopOverTitle() method
// Along with providing an element with the "popover-raw" class as a direct
// descendent of the component's root template
// They can then trigger showPopover; ie "@mouseover="showPopover""
// Note that once triggered, it will handle its own show/hide events

export default {
  props: {
    cellData: Object,
  },
  data: function () {
    return {
      showingPopOver: false,
    }
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('hideOtherPopOvers', this.responeToGlobalHide)
  },
  methods: {
    togglePopOver: function (event) {
      if (event.pointerType === 'touch') { // Don't response to clicks as taps
        if (this.showingPopOver) {
          // Need to give time to taps on links to register
          setTimeout(() => this.hidePopOver(), 150);
        } else {
          this.showPopOver()
        }
      }
    },
    getPopContent: function () {
      // Grab popover content from actual render html back as a string
      // Include the HTML explicitly in the template created problems
      var string = ''
      if (this.cellData.content.length > 0) {
        string += '<div class="list-group list-group-item-flush">'
        _.forEach(this.cellData.content, (item) => {
          string += '<div class="list-group-item">'
          if (item.link) {
            string += `<a href="${item.link}">${item.text}</a></div>`
          } else {
            string += `${item.text}</div>`
          }
        });
        string += '</div>'
      }
      return string
    },
    getPopTitle: function () {
      if (!_.isUndefined(this.cellData.title)) {
        return this.cellData.title
      }
      return ''
    },
    showPopOver: function () {

      if (this.showingPopOver) {
        return // This throws errors in Boostraps popover calls if not caught
      }

      $(this.$refs.container.$el).popover({
        animation: false,
        trigger: 'hover', // Dismiss handlers
        placement: 'bottom',
        fallbackPlacement: 'clockwise', // Can't be flip given overlap offsets
        html: true,
        title: this.getPopTitle,
        content: this.getPopContent,
        container: this.$refs.container.$el, // Must be same as event trigger
        offset: '0px, -12px', // Shift so hover is easier
      })
      $(this.$refs.container.$el).popover('show')

      // Wait until the show/hide actions finish before changing state
      let self = this
      $(this.$refs.container.$el).on('shown.bs.popover', () => {
        self.showingPopOver = true
        self.$eventHub.$emit('hideOtherPopOvers', self._uid)
      })
      $(this.$refs.container.$el).on('hidden.bs.popover', () => {
        self.showingPopOver = false
      })
    },
    hidePopOver: function () {
      if (this.showingPopOver) {
        $(this.$refs.container.$el).tooltip().popover('dispose');
        this.showingPopOver = false
      }
    },
    responeToGlobalHide(uid) {
      if (this._uid !== uid) {
        this.hidePopOver()
      }
    },
  },
}
</script>
