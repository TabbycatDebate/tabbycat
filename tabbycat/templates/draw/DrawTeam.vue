<template>
  <div :class="['hover-target', conflictsStatus,
                highlightsIdentity, highlightsStatus]"
       @mouseenter="showSlideOver(); showHoverConflicts()"
       @mouseleave="hideSlideOver(); hideHoverConflicts()">

    <div class="small d-flex justify-content-between">
      <div v-if="debugMode">
        {{ team.id }} {{ team.short_name }}<br>
        <span class="text-muted">
          {{ team.institution.id }} {{ team.institution.code }}
        </span>
      </div>
      <div v-else>
        {{ team.short_name }}
      </div>
      <div class="text-muted d-flex align-items-center" v-if="roundInfo.roundIsPrelim">
        <span>{{ liveness }}</span>
      </div>
    </div>

    <div class="history-tooltip tooltip" v-if="hasHistoryConflict">
      <div class="tooltip-inner conflictable"
           :class="'hover-histories-' + hasHistoryConflict + '-ago'">
        {{ hasHistoryConflict }} ago
      </div>
    </div>

  </div>
</template>

<script>
import SlideOverSubjectMixin from '../info/SlideOverSubjectMixin.vue'
import SlideOverTeamMixin from '../info/SlideOverTeamMixin.vue'
import HighlightableMixin from '../allocations/HighlightableMixin.vue'
import ConflictableMixin from '../allocations/ConflictableMixin.vue'

export default {
  data: function () {
    return {
      debugMode: false,
      // Adjs get this from Draggable(); teams must get it from there otherwise
      // it gets overwritten when merging options between Mixins
      isHovering: false
   }
  },
  mixins: [SlideOverSubjectMixin, SlideOverTeamMixin,
           HighlightableMixin, ConflictableMixin],
  props: { 'team': Object, 'roundInfo': Object },
  computed: {
    highlightableObject: function() {
      return this.team
    },
    liveness: function() {
      if (this.team.break_categories === null) {
        return ""
      }
      var short_code = ""
      for (var i = 0; i < this.team.break_categories.length; i++) {
        if ((this.team.break_categories[i].will_break === "live") ||
            (this.team.break_categories[i].will_break === "?")) {
          short_code += "☆"
        }
      }
      return short_code
    }
  },
}
</script>
