<template>

  <transition name="slide-over">
    <div class="panel slideover-info" v-if="subject">
      <div v-for="tier in subject.tiers" v-if="!tierIsEmpty(tier)"
           class="list-group-item flex-horizontal flex-justify">

        <div class="btn-toolbar flex-align-start">
          <div class="btn-group btn-group-sm mr-2">
            <slide-over-item v-for="item in tier.features[0]"
                             :key="item.id" :item="item">
            </slide-over-item>
          </div>
          <div class="btn-group btn-group-sm mr-2">
            <slide-over-item v-for="item in tier.features[1]"
                             :key="item.id" :item="item">
            </slide-over-item>
          </div>
        </div>

        <div class="btn-toolbar">
          <div class="btn-group btn-group-sm">
            <slide-over-item v-for="item in tier.features[2]"
                             :key="item.id" :item="item">
            </slide-over-item>
           </div>
        </div>

      </div>
    </div>
  </transition>

</template>

<script>
import SlideOverItem from './SlideOverItem.vue'

export default {
  components: { SlideOverItem },
  props: {
    subject: Object,
  },
  methods: {
    tierIsEmpty: function (tier) {
      const flattened = tier.features.reduce(
        function (accumulator, currentValue) {
          return accumulator.concat(currentValue)
        }, []
      )
      const flattenedNoNull = flattened.filter(item => item)
      return flattenedNoNull.length === 0
    },
  },
}
</script>
