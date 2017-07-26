<template>
  <div class="hover-target"
       @mouseenter="showSlideOver(venue)"
       @mouseleave="hideSlideOver">

    <span v-if="venue">{{ venue.name }}</span>

  </div>
</template>

<script>
import SlideOverSubjectMixin from '../../info/SlideOverSubjectMixin.vue'
import SlideOverVenueMixin from '../../info/SlideOverVenueMixin.vue'

export default {
  mixins: [SlideOverSubjectMixin, SlideOverVenueMixin],
  props: { 'venue': Object },
}
</script>
