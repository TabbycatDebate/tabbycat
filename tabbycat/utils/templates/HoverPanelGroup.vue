<template>

  <div class="btn-toolbar flex-nowrap">
    <div v-if="group.length > 0" v-for="group in groups" class="btn-group btn-group-sm mr-2">
      <button :class="['btn', item.css]" v-for="item in group">
        <i v-html="getFeatherIcon"></i>{{ item.title }}
      </button>
    </div>
  </div>

</template>

<script>
import FeatherMixin from '../../templates/tables/FeatherMixin.vue'

export default {
  mixins: [FeatherMixin],
  props: { groups: Array },
  computed: {
    icon: function () {
      if (this.item) {
        if ('icon' in this.item) {
          return this.item.icon
        }
      }
      return false
    },
  },
}
</script>
