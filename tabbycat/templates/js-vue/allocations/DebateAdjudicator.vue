<template>

  <div
    draggable=true
    v-on:dragstart="handleDragStart"
    v-on:dragend="handleDragEnd"
    v-on:mouseover="setHighlights"
    v-on:mouseout="unsetHighlights"
    v-bind:class="[isDragging ? vue-is-dragging : '', diversityHighlights, historiesHighlights, conflictsHighlights]"
    :id="adj.id"
    class="vue-draggable adj-draggable btn btn-default popover-parent">

      <div class="popover-anchor" v-on:mouseover="setupPopover"></div>

      <div class="h4">
        {{ letter_ranking }}
      </div>

      <div>
        <span>
          {{ short_name }}
        </span>
        <span class="small text-muted subtitle">
          <template v-if="adj.institution.code">
            {{ adj.institution.code }}
          </template>
          <template v-else>
            {{ adj.institution.name }}
          </template>
        </span>
      </div>

      <div class="popover-raw hide">
        <li class="list-group-item">
          Score of {{ adj.score }} (in the top {{ adj.ranking }})
        </li>
        <li class="list-group-item">
          {{ adj.gender_name }}
        </li>
        <li class="list-group-item">
          {{ adj.region ? '; ' + adj.region.name + ' Region': '' }}
        </li>
      </div>

    </div>

</template>

<script>
import PopoverMixin from '../mixins/PopoverMixin.vue'
import DraggableMixin from '../mixins/DraggableMixin.vue'
import AjaxMixin from '../mixins/AjaxMixin.vue'
import DiversityHighlightsMixin from '../mixins/DiversityHighlightsMixin.vue'
import ConflictsHighlightsMixin from '../mixins/ConflictsHighlightsMixin.vue'
import HistoriesHighlightsMixin from '../mixins/HistoriesHighlightsMixin.vue'

export default {
  mixins: [DraggableMixin, AjaxMixin, PopoverMixin, DiversityHighlightsMixin, HistoriesHighlightsMixin, ConflictsHighlightsMixin],
  props: {
    adj: Object,
    position: String,
    debateId: Number
  },
  computed: {
    short_name: function() {
      var names = this.adj.name.split(" ");
      return names[0] + " " + names[1][0] + ".";
    },
    letter_ranking: function() {
      if (this.adj.ranking === 10) {
        return "A+"
      } else if (this.adj.ranking === 10) {
        return "A "
      } else if (this.adj.ranking === 20) {
        return "A-"
      } else if (this.adj.ranking === 30) {
        return "B+"
      } else if (this.adj.ranking === 40) {
        return "B "
      } else if (this.adj.ranking === 50) {
        return "B-"
      } else if (this.adj.ranking === 60) {
        return "C+"
      } else if (this.adj.ranking === 70) {
        return "C"
      } else if (this.adj.ranking === 80) {
        return "C-"
      } else if (this.adj.ranking === 90) {
        return "F "
      } else if (this.adj.ranking === 100) {
        return "F "
      }
    }
  },
  methods: {
    getPopOverTitle: function() {
      return this.adj.name + " of " + this.adj.institution.name
    },
    getEntity: function() {
      return [this.adj, 'adj'];
    },
    setHighlights: function() {
      this.setConflictHighlights()
      this.setHistoriesHighlights()
    },
    unsetHighlights: function() {
      this.unsetConflictHighlights()
      this.unsetHistoriesHighlights()
    },
    handleDragStart: function(event) {
      // Set this adj's id as the data for receiving object
      this.$dispatch('set-dragged-adj', {
        'adj': this.adj,
        'position': this.position,
        'debateId': this.debateId
      })
    },
    handleDragEnd: function(event) {
      this.$dispatch('unset-dragged-adj')
    },
  },
  watch: {
    adj: function(newVal, oldVal) {
      // Call into the ajax mixing
      this.update(url, data, "adjudicator's allocation");
    }
  }
}
</script>
