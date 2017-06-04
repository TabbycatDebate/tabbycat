<template>
  <div draggable=true
       v-bind:class="[componentClasses, isDragging ? vue-is-dragging : '']"
       v-on:dragstart="handleDragStart"
       v-on:dragend="handleDragEnd"><!--
       v-on:mouseenter="show = true"
       v-on:mouseleave="show = false" -->

    <div class="draggable-prefix">
      <h4>{{ adjudicator.score }}</h4>
    </div>
    <div class="draggable-title">
      <h5 class="no-top-margin no-bottom-margin">{{ initialledName }}</h5>
      <span class="small text-muted subtitle">
        {{ adjudicator.insitution_name }}
      </span>
    </div>

  </div>
</template>

<script>
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import SlideOverSubjectMixin from '../infoovers/SlideOverSubjectMixin.vue'

export default {
  mixins: [DraggableMixin, SlideOverSubjectMixin],
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
