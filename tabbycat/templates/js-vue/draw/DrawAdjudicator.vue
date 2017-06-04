<template>
  <span v-on:mouseenter="showSlideOver(adjudicator)"
        v-on:mouseleave="hideSlideOver"
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
