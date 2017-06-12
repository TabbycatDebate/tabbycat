<template>
  <div :class="['slideover-target', conflictsStatus,
                highlightsIdentity, highlightsStatus]"
       @mouseenter="showSlideOver(team)"
       @mouseleave="hideSlideOver">

    <div><span>{{ team.short_name }}</span></div>

  </div>
</template>

<script>
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'
import SlideOverTeamMixin from '../infoovers/SlideOverTeamMixin.vue'
import HighlightableMixin from '../allocations/HighlightableMixin.vue'
import ConflictableMixin from '../allocations/ConflictableMixin.vue'

export default {
  mixins: [SlideOverSubjectMixin, SlideOverTeamMixin,
           HighlightableMixin, ConflictableMixin],
  props: { 'team': Object },
  computed: {
    highlightableObject: function() {
      return this.team
    }
  },
}
</script>
