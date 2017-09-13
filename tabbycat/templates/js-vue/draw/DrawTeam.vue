<template>
  <div :class="['hover-target', conflictsStatus,
                highlightsIdentity, highlightsStatus]"
       @mouseenter="handleHoverOn"
       @mouseleave="handleHoverOff">

    <div>
      <span class="small">
        <span v-if="debugMode">{{ team.id }}</span>
        {{ team.short_name }}
      </span>
    </div>

    <div class="history-tooltip tooltip" v-if="hasHistoryConflict">
      <div class="tooltip-inner conflictable hover-histories-1-ago">
        {{ hasHistoryConflict }} ago
      </div>
    </div>

  </div>
</template>

<script>
import SlideOverSubjectMixin from '../../info/SlideOverSubjectMixin.vue'
import SlideOverTeamMixin from '../../info/SlideOverTeamMixin.vue'
import HighlightableMixin from '../allocations/HighlightableMixin.vue'
import ConflictableMixin from '../allocations/ConflictableMixin.vue'

export default {
  data: function () {
    return { debugMode: true }
  },
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
      this.showHoverConflicts()
    },
    handleHoverOff: function(event) {
      this.hideSlideOver()
      this.hideHoverConflicts()
    },
  }
}
</script>
