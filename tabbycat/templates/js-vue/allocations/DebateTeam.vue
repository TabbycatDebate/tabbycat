<template>

  <div class="inline-flex bordered-bottom">
    <div class="debate-team flex-cell flex-vertical-center"
      v-bind:class="[diversityHighlights,
                     conflictsHighlights,
                     isHovering ? 'vue-is-hovering' : '']"
      v-on:mouseenter="setHighlights"
      v-on:mouseleave="unsetHighlights">
      <div class="history-tooltip tooltip top" v-if="historyHighlightText">
        <div class="tooltip-inner conflictable conflict-hover-{{ this.historyHighlightText }}-ago">
          saw {{ historyHighlightText }}
          round<span v-if="historyHighlightText > 1">s</span> ago
        </div>
      </div>
      <div class="flex-1">
        <p class="debate-team-title no-bottom-margin">
          <strong><span>{{ adjorteam.name }}</span></strong>
        </p>
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
              <template v-for="speaker in adjorteam.speakers">
                <div class="btn btn-default gender-display gender-{{ speaker.gender }}">
                  {{ speaker.name }}
                </div>
              </template>
            </div>
            <div class="btn-group btn-group-sm" role="group">
              <div class="btn btn-default region-display region-{{ adjorteam.region.seq }}">
                <span class="glyphicon glyphicon-globe"></span>
                  {{ adjorteam.institution.name }} {{ adjorteam.region.name }}
              </div>
            </div>
          </div>
          <div class="btn-toolbar pull-right">
            <div class="btn-group btn-group-sm pull-right" role="group" v-for="bc in adjorteam.categories">
              <div class="btn category-display category-{{ bc.seq }}">
                <span class="glyphicon glyphicon-globe"></span> {{ bc.name }}
              </div>
              <div class="btn btn-success" v-if="bc.will_break === true">
                SAFE ({{ adjorteam.wins }} Wins)
              </div>
              <div class="btn btn-default" v-if="bc.will_break === false">
                DEAD ({{ adjorteam.wins }} Wins)
              </div>
              <div class="btn btn-danger" v-if="bc.will_break === null">
                LIVE ({{ adjorteam.wins }} Wins)
              </div>
            </div>
          </div>
        </li>
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
