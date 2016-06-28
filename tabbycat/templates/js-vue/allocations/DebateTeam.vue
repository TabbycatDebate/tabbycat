<template>

  <div
    v-on:mouseover="setConflictHighlights"
    v-on:mouseout="unsetConflictHighlights"
    v-bind:class="[diversityHighlights, conflictsHighlights]"
    class="btn btn-default popover-parent">

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
          {{ team.region_name ? '; ' + team.region_name + ' Region' : '' }}
        </li>
        <li class="list-group-item">
          Break Categories
        </li>
      </div>

    </div>

</template>

<script>
import DiversityHighlightsMixin from '../mixins/DiversityHighlightsMixin.vue'
import ConflictsHighlightsMixin from '../mixins/ConflictsHighlightsMixin.vue'
import PopoverMixin from '../mixins/PopoverMixin.vue'

export default {
  mixins: [DiversityHighlightsMixin, ConflictsHighlightsMixin, PopoverMixin],
  props: {
    team: Object,
    currentConflictHighlights: Object
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
    }
  },
}
</script>
