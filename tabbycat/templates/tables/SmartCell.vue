<template>
  <td :class="cellData['class'] ? cellData['class'] : null">

    <span v-if="cellData['sort']" hidden>
      {{ cellData["sort"] }} <!-- Sorting key -->
    </span>

    <!-- Icons or Emoji -->
    <i v-if="cellData['icon']" :data-feather="cellData['icon']">
    </i>
    <span v-if="cellData['emoji']" class="emoji" >{{ cellData["emoji"] }}</span>

    <!-- Tooltip/Popovers Hovers Wrapper -->
    <span @mouseover="checkForPopoverOrTooltip"
      :class="[cellData['tooltip'] || cellData['popover'] ? 'hover-target' : '']">

      <!-- Links and modals -->
      <span v-if="cellData['link'] || cellData['modal']">
        <a v-if="cellData['link']" :href="cellData['link']" >
          <span v-html="cellData['text']"></span>
        </a>
        <a v-if="cellData['modal']" :data-target="cellData['modal']" >
          <span v-html="cellData['text']"></span>
        </a>
      </span>
      <span v-else>
        <span v-html="cellData['text']"></span>
      </span>

    </span>

    <span v-if="cellData['subtext']">
      <br><span class="small" v-html="cellData['subtext']"></span>
    </span>

    <div class="popover-raw" hidden v-if="canSupportPopover">
      <ul class="list-group list-group-item-flush">
        <li v-for="popItem in popOverContent" class="list-group-item">
          <a v-if="popItem['link']" :href="popItem['link']">
            <span v-html="popItem['text']"></span>
          </a>
          <span v-else>
            <span v-html="popItem['text']"></span>
          </span>
        </li>
      </ul>
    </div>

  </td>
</template>

<script>
import PopoverMixin from '../info/PopoverMixin.vue'

export default {
  mixins: [PopoverMixin],
  props: {
    cellData: Object,
  },
  computed: {
    canSupportPopover: function() {
      if (typeof this.cellData['popover'] !== 'undefined') {
        if (this.cellData['popover'].hasOwnProperty('content')) {
          return true
        }
      }
      return false
    },
    canSupportTooltip: function() {
      if (typeof this.cellData['tooltip'] !== 'undefined') {
        return true
      }
      return false
    },
    popOverContent: function () {
      if (this.canSupportPopover === true) {
        return this.cellData['popover']['content'].filter(function(key){
          return key['text'] !== ""
        });
      }
      return false
    }
  },
  methods: {
    getPopOverTitle: function() {
      return this.cellData['popover']['title']
    },
    checkForPopoverOrTooltip: function(event) {
      // Need to check the data exists for a popover before constructing it
      if (this.canSupportPopover === true) {
        var content = this.$el.getElementsByClassName('popover-raw')[0].innerHTML;
        this.setupPopover(event, content)
      } else if (this.canSupportTooltip === true) {
        // Manually construct/show a tooltip; doing it via jQuery doesn't
        // then update on table sorting as the DOM element is shifted
        $(event.target).tooltip({'title': this.cellData['tooltip']})
        $(event.target).tooltip('show')
      }
    }
  }
}
</script>
