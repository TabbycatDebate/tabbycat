<template>

  <div>

    <!-- Icons or Emoji -->
    <i v-if="icon" :class="cellData['iconClass']" v-html="getFeatherIcon"></i>
    <i v-if="cellData['emoji']" class="emoji" >{{ cellData["emoji"] }}</i>

    <!-- Links and modals -->
    <span v-if="cellData['link'] || cellData['modal']">
      <a v-if="cellData['link']" :href="cellData['link']" >
        <span class="tooltip-trigger" v-html="cellData['text']"></span>
      </a>
      <a v-if="cellData['modal']" :data-target="cellData['modal']" >
        <span class="tooltip-trigger" v-html="cellData['text']"></span>
      </a>
    </span>
    <span v-else>
      <span class="tooltip-trigger" v-html="cellData['text']"></span>
    </span>

    <span v-if="cellData['subtext']">
      <br><span class="small" v-html="cellData['subtext']"></span>
    </span>

  </div>

</template>

<script>
import FeatherMixin from './FeatherMixin.vue'
import _ from 'lodash'

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