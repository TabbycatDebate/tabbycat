<template>

  <div :class="[item.class, 'btn btn-outline-secondary']" >
    <i v-html="getFeatherIcon"></i>
    {{ item.title }}
  </div>

</template>

<script>
import FeatherMixin from '../tables/FeatherMixin.vue'
import _ from 'lodash'

export default {
  mixins: [ FeatherMixin ],
  props: { item: Object },
  computed: {
    icon: function() {
      if (!_.isUndefined(this.item.icon)) {
        return this.item.icon
      } else {
        return false
      }
    },
  }
}
</script>
