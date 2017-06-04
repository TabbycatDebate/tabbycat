<template>
  <div class="draw-cell flex-6 slideover-target"
       v-on:mouseenter="showSlideOver(team)"
       v-on:mouseleave="hideSlideOver">

    <span>{{ team.short_name }}</span>

  </div>
</template>

<script>
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'
import SlideOverTeamMixin from '../infoovers/SlideOverTeamMixin.vue'

export default {
  mixins: [SlideOverSubjectMixin, SlideOverTeamMixin],
  props: { 'team': Object },
}
</script>
