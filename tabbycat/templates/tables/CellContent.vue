<template>

  <div :data-toggle="cellData['tooltip'] ? tooltip : ''" :title="cellData['tooltip']">

    <!-- Icons or Emoji -->
    <i v-if="icon" :class="cellData['iconClass']" v-html="getFeatherIcon"></i>
    <i v-if="cellData['emoji']" class="emoji" >{{ cellData["emoji"] }}</i>

    <!-- Links and modals -->
    <template v-if="cellData['link'] || cellData['modal']">
      <a href="#" v-if="cellData['link']" :href="cellData['link']" >
        <span class="tooltip-trigger" v-html="cellData['text']"></span>
      </a>
      <a href="#" v-if="cellData['modal']" :data-target="cellData['modal']" >
        <span class="tooltip-trigger" v-html="cellData['text']"></span>
      </a>
    </template>

    <template v-else>
      <span class="tooltip-trigger" v-html="cellData['text']"></span>
    </template>

    <template v-if="cellData['subtext']">
      <br><span class="small" v-html="cellData['subtext']"></span>
    </template>

  </div>

</template>

<script>
import FeatherMixin from './FeatherMixin.vue'
import _ from 'lodash'

export default {
  mixins: [ FeatherMixin ],
  props: { cellData: Object },
  computed: {
    tooltip: function() {
      if (!_.isUndefined(this.cellData['tooltip'])) {
        return 'tooltip'
      } else {
        return false
      }
    },
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