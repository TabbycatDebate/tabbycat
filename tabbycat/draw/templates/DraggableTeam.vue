<template>
  <draggable-item :drag-payload="dragPayload" :class="{ 'bg-dark text-white': !item.available }">

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

export default {
  components: { DraggableItem },
  props: { item: Object, dragPayload: Object, isTrainee: false },
  computed: {
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
