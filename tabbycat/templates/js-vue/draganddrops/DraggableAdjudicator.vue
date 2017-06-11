<template>
  <div draggable=true
       :class="[draggableClasses, highlightsIdentity, highlightsStatus]"
       @dragstart="dragStart"
       @dragend="dragEnd"
       @mouseenter="showSlideOver(adjudicator)"
       @mouseleave="hideSlideOver"><!--
       @mouseenter="show = true"
       @mouseleave="show = false" -->

    <div class="draggable-prefix">
      <h4>{{ adjudicator.score }}</h4>
    </div>
    <div class="draggable-title">
      <h5 class="no-top-margin no-bottom-margin">{{ initialledName }}</h5>
      <span class="small text-muted subtitle" v-if="adjudicator.institution">
        {{ adjudicator.institution.code }}
      </span>
    </div>

  </div>
</template>

<script>
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'
import SlideOverAdjudicatorMixin from '../infoovers/SlideOverAdjudicatorMixin.vue'
import HighlightableMixin from '../allocations/HighlightableMixin.vue'

export default {
  mixins: [DraggableMixin, SlideOverSubjectMixin, SlideOverAdjudicatorMixin, HighlightableMixin],
  props: { 'adjudicator': Object, 'debateId': null},
  computed: {
    initialledName: function() {
      // Translate Joe Blogs into Joe B.
      var names = this.adjudicator.name.split(" ")
      if (names.length > 1) {
        var lastname = names[names.length - 1]
        var lastInitial = lastname[0]
        var firstNames = this.adjudicator.name.split(" " + lastname).join("")
        var limit = 10
        if (firstNames.length > limit + 2) {
          firstNames = firstNames.substring(0, limit) + "…"
        }
        return firstNames + " " + lastInitial
      }
      return names.join(" ")
    },
    highlightableObject: function() {
      return this.adjudicator
    },
    draggablePayload: function() {
      return JSON.stringify({ adjudicator: this.adjudicator.id, debate: this.debateId })
    }
  },
  methods: {
    handleDragStart: function(event) {
      // this.$dispatch('started-dragging-team', this);
    },
    handleDragEnd: function(event) {
      // this.$dispatch('stopped-dragging-team');
    },
  }
}
</script>
