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
      <h5 class="no-top-margin no-bottom-margin">{{ titleWithLimit }}</h5>
      <span class="small text-muted subtitle" v-for="c in venue.categories">
        {{ c.name }}
      </span>
      <span class="small text-muted subtitle" v-if="!venue.categories.length">
        N/A
      </span>
    </div>

  </div>
</template>

<script>
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import SlideOverSubjectMixin from '../../info/SlideOverSubjectMixin.vue'
import SlideOverVenueMixin from '../../info/SlideOverVenueMixin.vue'

export default {
  mixins: [DraggableMixin, SlideOverSubjectMixin, SlideOverVenueMixin],
  props: { 'venue': Object, 'debateId': null },
  computed: {
    titleWithLimit: function() {
      var limit = 18
      if (this.venue.name.length > limit + 2) {
        return this.venue.name.substring(0, limit) + "…"
      } else {
        return this.venue.name
      }
    },
    draggablePayload: function() {
      return JSON.stringify({ venue: this.venue.id, debate: this.debateId })
    }
  },
  methods: {
    handleDragStart: function(event) {
      // this.$dispatch('started-dragging-venue', this);
    },
    handleDragEnd: function(event) {
      // this.$dispatch('stopped-dragging-venue');
    },
  }
}
</script>
