<template>
  <div draggable=true
       :class="[draggableClasses]"
       @dragstart="dragStart"
       @dragend="dragEnd"
       @mouseenter="showSlideOver(venue)"
       @mouseleave="hideSlideOver">

    <div class="draggable-prefix">
      <h4>{{ venue.priority }}</h4>
    </div>

    <div class="draggable-title">
      <h5 class="mt-0 mb-0">{{ titleWithLimit }}</h5>
      <span v-for="c in venue.categories" :key="c.name"
            class="small text-muted subtitle" >
        {{ c.name }}
      </span>
      <span v-if="!venue.categories.length" class="small text-muted subtitle" >
        N/A
      </span>
    </div>

  </div>
</template>

<script>
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import SlideOverSubjectMixin from '../info/SlideOverSubjectMixin.vue'
import SlideOverVenueMixin from '../info/SlideOverVenueMixin.vue'

export default {
  mixins: [DraggableMixin, SlideOverSubjectMixin, SlideOverVenueMixin],
  props: { venue: Object, debateId: null },
  computed: {
    titleWithLimit: function () {
      const limit = 30
      if (this.venue.name.length > limit + 2) {
        return `${this.venue.name.substring(0, limit)}…`
      }
      return this.venue.name
    },
    draggablePayload: function () {
      return JSON.stringify({ venue: this.venue.id, debate: this.debateId })
    },
  },
  methods: {
    handleDragStart: function () {},
    handleDragEnd: function () {},
  },
}
</script>
