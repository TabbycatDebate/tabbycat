<template>

  <div class="hover-target" @click="showPopover" @mouseenter="showPopover">

    <slot>
      {{ content }}
    </slot>

  </div>

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
  methods: {
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
    showPopover: function (event) {
      // Popovers are disabled sometimes; e.g. on a scrolling draw page
      if ($(event.target).hasClass('disable-hover') === false) {
        $(event.target).popover({
          animation: true,
          trigger: 'hover click', // Dismiss handlers
          placement: 'bottom',
          html: true,
          title: this.getPopTitle,
          content: this.getPopContent,
          container: event.target, // Must be same as what triggers the event
          offset: '-25, 0', // Shift so hover is easier
        })
        $(event.target).popover('show')
      }
    },
    hidePopover: function (event) {
      $(event.target).popover('dispose'); // Now redundant; handle via trigger
    },
  },
}
</script>
