<template>
  <draggable-item :drag-payload="dragPayload" :class="[{'bg-dark text-white': isUnavailable},
                                                       highlightsCSS, conflictsCSS, hoverConflictsCSS]"
                  :enable-hover="true" :hover-item="hoverableData" :hover-type="hoverableType">

      <span slot="number" class="d-none"><span></span></span>
      <span slot="title" v-text="teamName"></span>
      <span slot="subtitle">
        <span>{{ institutionCode }}</span>
      </span>

  </draggable-item>
</template>

<script>
import { mapState } from 'vuex'
import DraggableItem from '../../templates/allocations/DraggableItem.vue'
import HighlightableMixin from '../../templates/allocations/HighlightableMixin.vue'
import HoverablePanelMixin from '../../templates/allocations/HoverablePanelMixin.vue'

export default {
  mixins: [HoverablePanelMixin, HighlightableMixin],
  components: { DraggableItem },
  props: {
    item: Object,
    dragPayload: Object,
    isTrainee: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    teamName: function () {
      let name = this.item.short_name // Default
      if (this.extra.codeNames === 'everywhere' || this.extra.codeNames === 'admin-tooltips-real') {
        name = this.item.code_name
        if (name === '') {
          name = this.gettext('No code name set')
        }
      }
      return name
    },
    isUnavailable: function () {
      if (this.$store.state.round.stage === 'E') {
        return false // Team availabilities are not set in break rounds so supress the coloring
      }
      return !this.item.available
    },
    highlightData: function () {
      return this.item
    },
    hoverableData: function () {
      return this.item
    },
    hoverableType: function () {
      return 'team'
    },
    institutionCode: function () {
      if (this.item.institution) {
        return this.$store.state.institutions[this.item.institution].code
      } else {
        return this.gettext('Unaffiliated')
      }
    },
    ...mapState(['extra']),
  },
}
</script>
