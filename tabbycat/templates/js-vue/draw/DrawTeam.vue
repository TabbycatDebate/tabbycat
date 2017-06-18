<template>
  <div :class="['slideover-target', conflictsStatus,
                highlightsIdentity, highlightsStatus]"
       @mouseenter="handleHoverOn"
       @mouseleave="handleHoverOff">

    <div><span>{{ team.short_name }}</span></div>

  </div>
</template>

<script>
import SlideOverSubjectMixin from '../../info/SlideOverSubjectMixin.vue'
import SlideOverTeamMixin from '../../info/SlideOverTeamMixin.vue'
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
  methods: {
    handleHoverOn: function(event) {
      this.showSlideOver()
      this.showConflicts()
    },
    handleHoverOff: function(event) {
      this.hideSlideOver()
      this.hideConflicts()
    },
  }
}
</script>
