<template>
  <div draggable=true
       :class="[draggableClasses, highlightsIdentity, highlightsStatus,
                isDragging ? vue-is-dragging : '']"
       @dragstart="handleDragStart"
       @dragend="handleDragEnd"
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
  props: {
    'adjudicator': Object,
    'show': { default: false }
  },
  computed: {
    initialledName: function() {
      // Translate Joe Blogs into Joe B.
      var names = this.adjudicator.name.split(" ")
      if (names.length > 1) {
        names[names.length - 1] = names[names.length - 1][0] + "."
      }
      return names.join(" ")
    },
    highlightableObject: function() {
      return this.adjudicator
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
