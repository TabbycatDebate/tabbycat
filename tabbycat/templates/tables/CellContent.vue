<template>

  <div class="flex-vertical-center">

    <!-- Icons or Emoji -->
    <i v-if="icon" :class="cellData.iconClass" v-html="getFeatherIcon"></i>
    <i v-if="cellData.emoji" class="emoji" >{{ cellData.emoji }}</i>

    <!-- Links and modals -->
    <div v-if="cellData.link || cellData.modal"
         :data-toggle="cellData.tooltip ? tooltip : ''" :title="cellData.tooltip">
      <a href="#" v-if="cellData.link" :href="cellData.link" >
        <span class="tooltip-trigger" v-html="cellData.text"></span>
      </a>
      <a href="#" v-if="cellData.modal" :data-target="cellData.modal" >
        <span class="tooltip-trigger" v-html="cellData.text"></span>
      </a>
      <small v-if="cellData.subtext" v-html="cellData.subtext"></small>
    </div>

    <!-- Standard -->
    <div v-else :data-toggle="cellData.tooltip ? tooltip : ''" :title="cellData.tooltip">
      <span class="tooltip-trigger" v-html="cellData.text"></span>
      <small v-if="cellData.subtext" v-html="cellData.subtext"></small>
    </div>

  </div>

</template>

<script>
import _ from 'lodash'
import FeatherMixin from './FeatherMixin.vue'

export default {
  mixins: [FeatherMixin],
  props: { cellData: Object },
  computed: {
    tooltip: function () {
      if (!_.isUndefined(this.cellData.tooltip)) {
        return 'tooltip'
      }
      return false
    },
    icon: function () {
      if (!_.isUndefined(this.cellData.icon)) {
        return this.cellData.icon
      }
      return false
    },
  },
}
</script>