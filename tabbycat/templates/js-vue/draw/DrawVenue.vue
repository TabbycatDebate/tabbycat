<template>
  <div class="slideover-target"
       v-on:mouseenter="showSlideOver(venue)"
       v-on:mouseleave="hideSlideOver">

    <span>{{ venue.name }}</span>

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
