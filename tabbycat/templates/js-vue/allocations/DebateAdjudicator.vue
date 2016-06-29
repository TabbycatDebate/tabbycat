<template>

  <div
    draggable=true
    v-on:dragstart="handleDragStart"
    v-on:dragend="handleDragEnd"
    v-on:mouseover="setHighlights"
    v-on:mouseout="unsetHighlights"
    v-bind:class="[isDragging ? vue-is-dragging : '', diversityHighlights, historiesHighlights, conflictsHighlights]"
    class="vue-draggable adj-draggable btn btn-default popover-parent">

      <div class="popover-anchor" v-on:mouseover="setupPopover"></div>

      <div class="h4">
        {{ adj.score }}
      </div>

      <div>
        <span>
          {{ short_name }}
        </span>
        <span class="small text-muted">
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
    currentConflictHighlights: Object,
    currentHistoriesHighlights: Array
  },
  computed: {
    short_name: function() {
      var names = this.adj.name.split(" ");
      return names[0] + " " + names[1][0] + ".";
    },
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
    }
  },
  watch: {
    adj: function(newVal, oldVal) {
      // Call into the ajax mixing
      this.update(url, data, "adjudicator's allocation");
    }
  }
}
</script>
