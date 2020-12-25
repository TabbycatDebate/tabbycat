<template>

  <transition name="slide-over">
    <div class="panel slideover-info" v-if="this.subject">
      <template v-if="panelRows">
        <div v-for="row in panelRows" class="list-group-item flex-horizontal pl-2 flex-justify">
          <div class="flex-align-start">
            <hover-panel-group :groups="row['left']"></hover-panel-group>
          </div>
          <div>
            <hover-panel-group :groups="row['right']"></hover-panel-group>
          </div>
        </div>
      </template>
    </div>
  </transition>

</template>

<script>
import { mapState, mapGetters } from 'vuex'
import HoverPanelTeamMixin from './HoverPanelTeamMixin.vue'
import HoverPanelAdjudicatorMixin from './HoverPanelAdjudicatorMixin.vue'
import HoverPanelSharedMixin from './HoverPanelSharedMixin.vue'
import HoverPanelGroup from './HoverPanelGroup.vue'

export default {
  components: { HoverPanelGroup },
  mixins: [HoverPanelTeamMixin, HoverPanelAdjudicatorMixin, HoverPanelSharedMixin],
  computed: {
    subject: function () {
      return this.hoverSubject
    },
    panelRows: function () {
      return [this.topRow, this.bottomRow]
    },
    topRow: function () {
      const leftFeatures = this.hoverType ? this['topleft' + this.hoverType] : []
      const rightFeatures = this.hoverType ? this['topright' + this.hoverType] : []
      return { left: leftFeatures, right: rightFeatures }
    },
    bottomRow: function () {
      const leftFeatures = this.hoverType ? this['bottomleft' + this.hoverType] : []
      const rightFeatures = this.hoverType ? this['bottomright' + this.hoverType] : []
      return { left: leftFeatures, right: rightFeatures }
    },
    ...mapState(['hoverSubject', 'hoverType', 'highlights', 'extra']),
    ...mapGetters(['allTeams', 'allInstitutions', 'allAdjudicators']),
  },
}
</script>
