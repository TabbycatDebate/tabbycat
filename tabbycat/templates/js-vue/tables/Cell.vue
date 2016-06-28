<template>

  <td :class="cellData['class'] ? cellData['class'] : null">

    <!-- Sorting key -->
    <span v-if="cellData['sort']" class="hidden">
      {{ cellData["sort"] }}
    </span>
    <!-- Icons or Emoji -->
    <span v-if="cellData['icon']" class="glyphicon" :class="cellData['icon']">
    </span>
    <span v-if="cellData['emoji']" class="emoji" >
      {{ cellData["emoji"] }}
    </span>

    <!-- Tooltip/Popovers Hovers Wrapper -->
    <span
      :title="cellData['tooltip']"
      :data-toggle="cellData['popover'] || cellData['tooltip'] ? 'tooltip' : ''"
      v-on:mouseover="checkForPopover">

      <!-- Links and modals -->
      <template v-if="cellData['link'] || cellData['modal']">
        <a v-if="cellData['link']" :href="cellData['link']" >
          <span v-html="cellData['text']"></span>
        </a>
        <a v-if="cellData['modal']" :data-target="cellData['modal']" >
          <span v-html="cellData['text']"></span>
        </a>
      </template>
      <template v-else>
        <span v-html="cellData['text']"></span>
      </template>

    </span>

    <template v-if="cellData['subtext']">
      <br><span class="small" v-html="cellData['subtext']"></span>
    </template>

    <div class="popover-raw hide" v-if="cellData['popover']">
      <li v-for="popContent in cellData['popover']['content']" class="list-group-item">
        <a v-if="popContent['link']" :href="popContent['link']">
          {{ popContent['text'] }}
        </a>
        <span v-else>
          {{ popContent['text'] }}
        </span>
      </li>
    </div>

  </td>

</template>

<script>
import Popover from '../mixins/Popover.vue'

export default {
  mixins: [Popover],
  props: {
    cellData: Object,
  },
  methods: {
    getPopOverTitle: function() {
      return this.cellData['popover']['title'];
    },
    checkForPopover: function(event) {
      // Need to check the data exists for a popover before constructing it
      if (typeof this.cellData['popover'] !== 'undefined') {
        this.setupPopover(event);
      }
    },
  }
}
</script>
