<template>
  <div draggable=true
       :class="[draggableClasses, conflictsStatus, highlightsIdentity,
                highlightsStatus, 'ranking-' + percentileRanking.percentile]"
       @dragstart="dragStart"
       @dragend="dragEnd"
       @mouseenter="showSlideOver(); showHoverConflicts()"
       @mouseleave="hideSlideOver(); hideHoverConflicts()">

    <div class="draggable-prefix">
      <h4 v-html="shrunkScore"></h4>
    </div>
    <div class="draggable-title">
      <h5 class="mt-0 mb-0">
        <span v-if="debugMode">{{ adjudicator.id }} </span>{{ initialledName }}
      </h5>
      <span class="small subtitle" v-if="adjudicator.institution">
        <span v-if="debugMode">{{ adjudicator.institution.id }}</span>
        {{ adjudicator.institution.code }}
      </span>
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
import _ from 'lodash'
import DraggableMixin from '../draganddrops/DraggableMixin.vue'
import SlideOverSubjectMixin from '../info/SlideOverSubjectMixin.vue'
import SlideOverAdjudicatorMixin from '../info/SlideOverAdjudicatorMixin.vue'
import HighlightableMixin from '../allocations/HighlightableMixin.vue'
import ConflictableMixin from '../allocations/ConflictableMixin.vue'

export default {
  mixins: [DraggableMixin, SlideOverSubjectMixin, SlideOverAdjudicatorMixin,
           HighlightableMixin, ConflictableMixin],
  props: { 'adjudicator': Object, 'debateId': null, 'percentiles': Array },
  data: function () {
    return { debugMode: false }
  },
  computed: {
    initialledName: function () {
      // Translate Joe Blogs into Joe B.
      var names = this.adjudicator.name.split(" ")
      if (names.length > 1) {
        var lastname = names[names.length - 1]
        var lastInitial = lastname[0]
        var firstNames = this.adjudicator.name.split(" " + lastname).join('')
        var limit = 10
        if (firstNames.length > limit + 2) {
          firstNames = firstNames.substring(0, limit) + "…"
        }
        return firstNames + " " + lastInitial
      }
      return names.join(" ")
    },
    shrunkScore: function () {
      var score = this.adjudicator.score.split(".")[0]
      score += "<small>." + this.adjudicator.score.split(".")[1] + "</small>"
      return score
    },
    highlightableObject: function () {
      return this.adjudicator
    },
    draggablePayload: function () {
      return JSON.stringify({ adjudicator: this.adjudicator.id, debate: this.debateId })
    },
    percentileRanking: function () {
      var rating = parseFloat(this.adjudicator.score)
      var rank =  _.find(this.percentiles, function (threshold) {
        return rating >= threshold.cutoff
      })
      if (_.isUndefined(rank)) {
        // Sometimes a score might be weird like in the negatives; in which case
        // just give them the lowest possible percentile to avoid an error
        rank = this.percentiles[this.percentiles.length - 1]
      }
      if (rank.percentile > 50) {
        var percentileText = ' Ranking (Top ' + (100 - rank.percentile) + '%)'
      } else {
        var percentileText = ' Ranking (Bottom ' + rank.percentile + '%)'
      }
      return { 'grade': rank.grade, 'percentile': rank.percentile, 'text': percentileText}
    }
  },
  methods: {
    handleDragStart: function (event) {
      // this.$dispatch('started-dragging-team', this);
    },
    handleDragEnd: function (event) {
      this.hideHoverConflicts()
      this.hideSlideOver()
    },
  }
}
</script>
