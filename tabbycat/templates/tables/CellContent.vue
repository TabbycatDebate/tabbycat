<template>

  <div>

    <!-- Icons or Emoji -->
    <i v-if="cellData['icon']" :class="cellData['iconClass']"
       v-html="getFeatherIcon"></i>
    <i v-if="cellData['emoji']" class="emoji" >{{ cellData["emoji"] }}</i>

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

  </div>

</template>

<script>
import feather from 'feather-icons';

export default {
  props: { cellData: Object },
  computed: {
    getFeatherIcon: function() {
      // Need to dynamically update icons once table order changes
      // as they are otherwise tied to the DOM
      if (this.cellData.hasOwnProperty('icon')) {
        return feather.toSvg(this.cellData['icon']);
      }
      return false
    },
  }
}
</script>