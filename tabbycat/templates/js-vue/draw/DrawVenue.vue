<template>
  <div class="slideover-target"
       @mouseenter="showSlideOver(venue)"
       @mouseleave="hideSlideOver">

    <span v-if="venue">{{ venue.name }}</span>

  </div>
</template>

<script>
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'
import SlideOverVenueMixin from '../infoovers/SlideOverVenueMixin.vue'

export default {
  mixins: [SlideOverSubjectMixin, SlideOverVenueMixin],
  props: { 'venue': Object },
}
</script>
