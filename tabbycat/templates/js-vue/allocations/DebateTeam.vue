<template>

  <div class="debate-team flex-cell flex-vertical-center bordered-bottom"
    v-on:mouseover="setHighlights"
    v-on:mouseout="unsetHighlights"
    v-bind:class="[diversityHighlights, historiesHighlights,
                   conflictsHighlights]">

    <div class="flex-1 slideover-parent">

      <div class="slideover-anchor" v-on:mouseover=""></div>

      <div class="">
        <p class="debate-team-title no-bottom-margin">
          <strong>{{ adjorteam.name }}</strong>
        </p>
        <template v-for="bc in adjorteam.categories">
          <span v-if="bc.will_break === true" class=" small subtitle text-success">
            SAFE ({{ adjorteam.wins }} Wins)
          </span>
          <span v-if="bc.will_break === false" class=" small subtitle text-muted">
            DEAD ({{ adjorteam.wins }} Wins)
          </span>
          <span v-if="bc.will_break === null" class=" small subtitle text-danger">
            LIVE ({{ adjorteam.wins }} Wins)
          </span>
        </template>
      </div>

      <div class="slideover-info slideover-top">
        <li class="list-group-item flex-horizontal">

          <div class="flex-1 btn-toolbar">
            <div class="btn-group btn-group-sm " role="group">
              <div class="btn btn-default">{{ adjorteam.speakers }}</div>
            </div>
          </div>

          <h4 class="flex-1 slideover-title text-center">
            {{ adjorteam.long_name }}
          </h4>

          <div class="flex-1 btn-toolbar">

            <div class="btn-group btn-group-sm pull-right" role="group">
              <div class="btn btn-default region-display region-{{ adjorteam.region.seq }}">
                <span class="glyphicon glyphicon-globe"></span>
              </div>
              <div class="btn btn-default btn-sm">
                {{ adjorteam.region.name }}
              </div>
            </div>

            <div class="btn-group btn-group-sm pull-right" role="group" v-for="category in adjorteam.categories">
              <div class="btn btn-default">
                <span class="glyphicon glyphicon-globe category-display category-{{ category.seq }}"></span>
              </div>
              <div class="btn btn-default btn-sm">
                {{ category.name }} Break
              </div>
            </div>

          </div>
        </li>
        <li class="list-group-item">

          seen history

        </li>
      </div>

    </div>
  </div>

</template>

<script>
import DiversityHighlightsMixin from '../mixins/DiversityHighlightsMixin.vue'
import ConflictsHighlightsMixin from '../mixins/ConflictsHighlightsMixin.vue'
import HistoriesHighlightsMixin from '../mixins/HistoriesHighlightsMixin.vue'

export default {
  mixins: [DiversityHighlightsMixin, ConflictsHighlightsMixin, HistoriesHighlightsMixin],
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
