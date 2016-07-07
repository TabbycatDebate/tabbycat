<template>

  <div class="inline-flex">
    <div
      draggable=true
      v-on:dragstart="handleDragStart"
      v-on:dragend="handleDragEnd"
      v-on:mouseenter="setHighlights"
      v-on:mouseleave="unsetHighlights"
      v-bind:class="[isDragging ? 'vue-is-dragging' : '', diversityHighlights,
                     historiesHighlights, conflictsHighlights]"
      :id="adjorteam.id"
      class="vue-draggable adj-draggable btn btn-default popover-parent">

      <div class="h4 adj-score">
        {{ letter_ranking }}
      </div>

      <div class="history-tooltip tooltip left" v-if="adjorteam.hasHistoryConflict">
        <div class="tooltip-arrow"></div>
        <div class="tooltip-inner">
          {{ adjorteam.historyRoundsAgo }}<br>ago
        </div>
      </div>

      <div class="adj-info">
        <span>
          {{ short_name }}
        </span>
        <span class="small text-muted subtitle">
          <template v-if="adjorteam.institution.code">
            {{ adjorteam.institution.code }}
          </template>
          <template v-else>
            {{ adjorteam.institution.name }}
          </template>
        </span>
      </div>
    </div>

    <div class="panel slideover-top"
        :class="{ 'slideover-info': showSlideOver}"
        v-if="showSlideOver"
        transition="expand">
      <div class="list-group">
        <li class="list-group-item">
          <h4 class="no-bottom-margin no-top-margin text-center">
            {{ adjorteam.name }} ({{ adjorteam.institution.name }})
          </h4>
        </li>
        <li class="list-group-item flex-horizontal">
          <div class="flex-1 btn-toolbar">
            <div class="btn-group btn-group-sm " role="group">
              <div class="btn btn-default gender-display gender-{{ adjorteam.gender }}">
                {{ adjorteam.name }}
              </div>
            </div>
            <div class="btn-group btn-group-sm" role="group">
              <div class="btn btn-default region-display region-{{ adjorteam.region.seq }}">
                <span class="glyphicon glyphicon-globe"></span>
                {{ adjorteam.institution.name }} {{ adjorteam.region.name }}
              </div>
            </div>
          </div>
          <div class="btn-toolbar pull-right">
            <div class="btn-group btn-group-sm " role="group">
              <div class="btn btn-default">
                {{ adjorteam.score }}
              </div>
              <div class="btn btn-default">
                Feedback Rating
              </div>
            </div>
            <div class="btn-group btn-group-sm " role="group">
              <div class="btn btn-default">
                {{ letter_ranking }}
              </div>
              <div class="btn btn-default">
                Feedback Scale ({{ adjorteam.ranking }}th Percentile)
              </div>
            </div>
          </div>
        </li>
      </div>
    </div>
  </div>


</template>

<script>
import DraggableMixin from '../mixins/DraggableMixin.vue'
import AjaxMixin from '../mixins/AjaxMixin.vue'
import DiversityHighlightsMixin from '../mixins/DiversityHighlightsMixin.vue'
import ConflictsHighlightsMixin from '../mixins/ConflictsHighlightsMixin.vue'

export default {
  mixins: [DraggableMixin, AjaxMixin, DiversityHighlightsMixin, ConflictsHighlightsMixin],
  props: {
    adjorteam: Object,
    position: String,
    debateId: Number,
    showSlideOver: { default: false }
  },
  computed: {
    short_name: function() {
      var names = this.adjorteam.name.split(" ");
      return names[0] + " " + names[1][0] + ".";
    },
    letter_ranking: function() {
      if (this.adjorteam.ranking === 10) {
        return "A+"
      } else if (this.adjorteam.ranking === 10) {
        return "A "
      } else if (this.adjorteam.ranking === 20) {
        return "A-"
      } else if (this.adjorteam.ranking === 30) {
        return "B+"
      } else if (this.adjorteam.ranking === 40) {
        return "B "
      } else if (this.adjorteam.ranking === 50) {
        return "B-"
      } else if (this.adjorteam.ranking === 60) {
        return "C+"
      } else if (this.adjorteam.ranking === 70) {
        return "C"
      } else if (this.adjorteam.ranking === 80) {
        return "C-"
      } else if (this.adjorteam.ranking === 90) {
        return "F "
      } else if (this.adjorteam.ranking === 100) {
        return "F "
      }
    }
  },
  methods: {
    setHighlights: function() {
      this.setConflictHighlights('set-hover-conflicts')
      this.showSlideOver = true
    },
    unsetHighlights: function() {
      this.unsetConflictHighlights('unset-hover-conflicts')
      this.showSlideOver = false
    },
    handleDragStart: function(event) {
      // Set this adj's id as the data for receiving object
      this.$dispatch('set-dragged-adj', {
        'adj': this.adjorteam,
        'position': this.position,
        'debateId': this.debateId
      })
    },
    handleDragEnd: function(event) {
      this.$dispatch('unset-dragged-adj')
    },
  },
  watch: {
    adjorteam: function(newVal, oldVal) {
      // Call into the ajax mixing
      this.update(url, data, "adjudicator's allocation");
    }
  }
}
</script>
