<template>

  <div class="flex-1 flex-vertical-center bordered-bottom"
    v-on:mouseover="setHighlights"
    v-on:mouseout="unsetHighlights"
    v-bind:class="[diversityHighlights, historiesHighlights,
                   conflictsHighlights]">

    <div class="flex-1 popover-parent">

      <div class="popover-anchor" v-on:mouseover="setupPopover"></div>

      <div class="">
        <strong class="debate-team-name">{{ adjorteam.name }}</strong><br>
        <span class="small text-muted">{{ adjorteam.wins }} Wins</span>
      </div>

      <div class="popover-raw hide">
        <li class="list-group-item">
          {{ adjorteam.speakers }}
        </li>
        <li class="list-group-item">
          {{ adjorteam.gender_name }}
          {{ adjorteam.region ? '; ' + adjorteam.region.name + ' Region' : '' }}
        </li>
        <li class="list-group-item" v-if="adjorteam.categories">
          <span v-for="bc in adjorteam.categories">
            {{ bc.name }}
          </span>
        </li>
      </div>

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
    adjorteam: Object
  },
  methods: {
    getPopOverTitle: function() {
      if (this.adjorteam.uses_prefix === true) {
        return this.adjorteam.long_name
      } else {
        return this.adjorteam.long_name + " of " + this.adjorteam.institution.name
      }
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
