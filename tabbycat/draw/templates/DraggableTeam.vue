<template>
  <draggable-item :drag-payload="dragPayload" :class="{ 'bg-dark text-white': !item.available }"
                  :enable-hover="true" :hover-item="hoverableData" :hover-type="hoverableType">

      <span slot="number" class="d-none"><span></span></span>
      <span slot="title">
        {{ item.short_name }}
      </span>
      <span slot="subtitle">
        <span>{{ institutionCode }}</span>
      </span>

  </draggable-item>
</template>

<script>
import DraggableItem from '../../utils/templates/DraggableItem.vue'
import HighlightableMixin from '../../utils/templates/HighlightableMixin.vue'
import HoverableMixin from '../../utils/templates/HoverableMixin.vue'

export default {
  mixins: [HoverableMixin, HighlightableMixin],
  components: { DraggableItem },
  props: { item: Object, dragPayload: Object, isTrainee: false },
  computed: {
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
  },
}
</script>
