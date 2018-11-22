<template>
  <span @mouseenter="showSlideOver(adjudicator)"
        @mouseleave="hideSlideOver"
        class="hover-target">

    <span>{{ adjudicator.name }} ({{ position }})</span>,

  </span>
</template>

<script>
import SlideOverSubjectMixin from '../info/SlideOverSubjectMixin.vue'
import SlideOverAdjudicatorMixin from '../info/SlideOverAdjudicatorMixin.vue'

export default {
  mixins: [SlideOverSubjectMixin, SlideOverAdjudicatorMixin],
  props: {
    adjudicator: Object,
    position: String,
  },
}
</script>
