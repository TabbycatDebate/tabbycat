<template>

  <div
    v-on:mouseover="setHighlights"
    v-on:mouseout="unsetHighlights"
    v-bind:class="[diversityHighlights, historiesHighlights, conflictsHighlights]"
    class="popover-parent">

      <div class="popover-anchor" v-on:mouseover="setupPopover"></div>

      <div class="">
        {{ team.name }}
      </div>

      <div class="popover-raw hide">
        <li class="list-group-item">
          {{ team.speakers }}
        </li>
        <li class="list-group-item">
          {{ team.gender_name }}
          {{ team.region ? '; ' + team.region.name + ' Region' : '' }}
        </li>
        <li class="list-group-item" v-if="team.categories">
          <span v-for="bc in team.categories">
            {{ bc.name }}
          </span>
        </li>
      </div>

    </div>

</template>

<script>
import DiversityHighlightsMixin from '../mixins/DiversityHighlightsMixin.vue'
import ConflictsHighlightsMixin from '../mixins/ConflictsHighlightsMixin.vue'
import HistoriesHighlightsMixin from '../mixins/HistoriesHighlightsMixin.vue'
import PopoverMixin from '../mixins/PopoverMixin.vue'

export default {
  mixins: [DiversityHighlightsMixin, ConflictsHighlightsMixin, HistoriesHighlightsMixin, PopoverMixin],
  props: {
    team: Object,
    currentConflictHighlights: Object,
    currentHistoriesHighlights: Array
  },
  methods: {
    getPopOverTitle: function() {
      if (this.team.uses_prefix === true) {
        return this.team.long_name
      } else {
        return this.team.long_name + " of " + this.team.institution.name
      }
    },
    getEntity: function() {
      return [this.team, 'team'];
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
}
</script>
