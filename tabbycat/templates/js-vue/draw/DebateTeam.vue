<template>

  <div class="inline-flex bordered-bottom tooltip-holder">
    <div class="debate-team flex-cell flex-vertical-center"
      v-bind:class="[diversityHighlights, diversityState,
                     conflictsHighlights,
                     isHovering ? 'vue-is-hovering' : '']"
      v-on:mouseenter="setHighlights"
      v-on:mouseleave="unsetHighlights">
      <div class="history-tooltip tooltip" v-if="historyHighlightText">
        <div v-bind:class="'tooltip-inner conflictable conflict-hover-' + this.historyHighlightText + '-ago'">
          {{ historyHighlightText }} ago
        </div>
      </div>
      <div class="flex-1">
        <p class="debate-team-title no-bottom-margin">
          <strong><span>{{ adjorteam.name }}</span></strong>
        </p>
      </div>
    </div>
  </div>

</template>

<script>
import DiversityHighlightsMixin from '../mixins/DiversityHighlightsMixin.vue'
import ConflictsHighlightsMixin from '../mixins/ConflictsHighlightsMixin.vue'

export default {
  mixins: [DiversityHighlightsMixin, ConflictsHighlightsMixin],
  props: {
    adjorteam: Object,
    showSlideOver: { default: false }
  },
  methods: {
    setHighlights: function() {
      this.setConflictHighlights('set-hover-conflicts')
      this.showSlideOver = true
      this.isHovering = true;
    },
    unsetHighlights: function() {
      this.unsetConflictHighlights('unset-hover-conflicts')
      this.showSlideOver = false
      this.isHovering = false;
    }
  },
}
</script>
