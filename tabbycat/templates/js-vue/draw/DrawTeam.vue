<template>
  <div class="slideover-target"
       @mouseenter="showSlideOver(team)"
       @mouseleave="hideSlideOver">

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
