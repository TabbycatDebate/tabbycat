<template>
  <span @mouseenter="showSlideOver(adjudicator)"
        @mouseleave="hideSlideOver"
        class="slideover-target">

    <span>{{ adjudicator.name }} ({{ position }})</span>,

  </span>
</template>

<script>
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'
import SlideOverAdjudicatorMixin from '../infoovers/SlideOverAdjudicatorMixin.vue'

export default {
  mixins: [SlideOverSubjectMixin, SlideOverAdjudicatorMixin],
  props: { 'adjudicator': Object,
           'position': String },
}
</script>
