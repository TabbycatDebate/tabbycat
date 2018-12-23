<template>

  <transition name="slide-over">
    <div class="panel slideover-info" v-if="this.subject">

      <div v-if="row" v-for="row in rows" class="list-group-item flex-horizontal pl-2 flex-justify">
        <div class="btn-toolbar flex-align-start">
          <hover-panel-group :groups="row['left']"></hover-panel-group>
        </div>
        <div class="btn-toolbar">
          <hover-panel-group :groups="row['right']"></hover-panel-group>
        </div>
      </div>

    </div>
  </transition>

</template>

<script>
import { mapState } from 'vuex'
import HoverPanelTeamMixin from './HoverPanelTeamMixin.vue'
import HoverPanelAdjudicatorMixin from './HoverPanelAdjudicatorMixin.vue'
import HoverPanelSharedMixin from './HoverPanelSharedMixin.vue'
import HoverPanelGroup from './HoverPanelGroup.vue'

export default {
  components: { HoverPanelGroup },
  mixins: [ HoverPanelTeamMixin, HoverPanelAdjudicatorMixin, HoverPanelSharedMixin ],
  computed: {
    subject: function () {
      return this.hoverSubject
    },
    rows: function () {
      return [this.topRow, this.bottomRow]
    },
    topRow: function () {
      let leftFeatures = this.hoverType ? this['topleft' + this.hoverType] : []
      let rightFeatures = this.hoverType ? this['topright' + this.hoverType] : []
      return { left: leftFeatures, right: rightFeatures }
    },
    bottomRow: function () {
      let leftFeatures = this.hoverType ? this['bottomleft' + this.hoverType] : []
      let rightFeatures = this.hoverType ? this['bottomright' + this.hoverType] : []
      return { left: leftFeatures, right: rightFeatures }
    },
    ...mapState(['hoverSubject', 'hoverType', 'highlights', 'institutions']),
  },
}
</script>
