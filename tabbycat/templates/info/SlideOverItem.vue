<template>

  <button :class="[item.class, 'btn btn-outline-secondary']" >
    <i v-html="getFeatherIcon"></i>
    {{ item.title }}
  </button>

</template>

<script>
import _ from 'lodash'
import FeatherMixin from '../tables/FeatherMixin.vue'

export default {
  mixins: [FeatherMixin],
  props: { item: Object },
  computed: {
    icon: function () {
      if (!_.isUndefined(this.item.icon)) {
        return this.item.icon
      }
      return false
    },
  },
}
</script>
