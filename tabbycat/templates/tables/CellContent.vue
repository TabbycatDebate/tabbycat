<template>

  <div>

    <!-- Icons or Emoji -->
    <i :class="cellData['iconClass']" v-html="getFeatherIcon">ICON</i>
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

    <span v-if="cellData['subtext']">
      <br><span class="small" v-html="cellData['subtext']"></span>
    </span>

  </div>

</template>

<script>
import FeatherMixin from './FeatherMixin.vue'
import _ from 'lodash'
import feather from 'feather-icons';

export default {
  mixins: [ FeatherMixin ],
  props: { cellData: Object },
  computed: {
    icon: function() {
      if (!_.isUndefined(this.cellData['icon'])) {
        return this.cellData['icon']
      } else {
        return false
      }
    },
  }
}
</script>