<template>
  <div :class="['slideover-target', highlightsIdentity, highlightsStatus]"
       @mouseenter="showSlideOver(team)"
       @mouseleave="hideSlideOver">

    <div><span>{{ team.short_name }}</span></div>

  </div>
</template>

<script>
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'
import SlideOverTeamMixin from '../infoovers/SlideOverTeamMixin.vue'
import HighlightableMixin from '../allocations/HighlightableMixin.vue'

export default {
  mixins: [SlideOverSubjectMixin, SlideOverTeamMixin, HighlightableMixin],
  props: { 'team': Object },
  computed: {
    highlightableObject: function() {
      return this.team
    }
  },
}
</script>
