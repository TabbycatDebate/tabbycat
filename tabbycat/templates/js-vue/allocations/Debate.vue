<template>
  <div class="row flex-horizontal">

    <div class="flex-cell flex-vertical-center bordered-bottom">
      <div class="flex-1">{{ debate.bracket }}</div>
    </div>

    <div class="flex-cell importance-container flex-vertical-center bordered-bottom">
      <div class="flex-1">
        <debate-importance
          :id="debate.id"
          :importance="debate.importance"
          :url="debate.importance_url">
        </debate-importance>
      </div>
    </div>

    <div class="flex-1 flex-vertical-center bordered-bottom">
      <div class="flex-1">
        <debate-team :team="aff"></debate-team>
      </div>
    </div>

    <div class="flex-1 flex-vertical-center bordered-bottom">
      <div class="flex-1">
        <debate-team :team="neg"></debate-team>
      </div>
    </div>

    <div class="flex-8">
      <div class="panel panel-default panel-debate">
        <div class="flex-horizontal positions-parent">

          <position-droppable
            :adjudicators="debateAdjudicators.chair"
            :debate-id="debate.id"
            :position="'C'">
          </position-droppable>
          <position-droppable
            :adjudicators="debateAdjudicators.panelists"
            :debate-id="debate.id"
            :position="'P'">
          </position-droppable>
          <position-droppable
            :adjudicators="debateAdjudicators.trainees"
            :debate-id="debate.id"
            :position="'T'">
          </position-droppable>

        </div>
      </div>
    </div>

    <div class="flex-cell flex-vertical-center bordered-bottom">
      <div class="flex-1">
        {{ panelScore }}
      </div>
    </div>

  </div>
</template>

<script>
import DebateTeam from './DebateTeam.vue'
import DebateImportance from './DebateImportance.vue'
import PositionDroppable from './PositionDroppable.vue'

export default {
  components: {
    DebateTeam, DebateImportance, PositionDroppable
  },
  props: {
    allAdjudicators: Object,
    debate: Object,
    aff: Object,
    neg: Object
  },
  computed: {
    debateAdjudicators: function () {
      var panel = this.debate.panel;
      var debateAdjudicators = {
        chair: [],
        panelists: [],
        trainees: []
      }
      for (var i = 0; i < panel.length; ++i) {
        var foundAdj = this.allAdjudicators[panel[i].id]
        if (panel[i].position === "C") {
          debateAdjudicators.chair.push(foundAdj);
        } else if (panel[i].position === "P") {
          debateAdjudicators.panelists.push(foundAdj);
        } else if (panel[i].position === "T") {
          debateAdjudicators.trainees.push(foundAdj);
        }
      }
      return debateAdjudicators;
    },
    panelScore: function () {
      if (typeof this.panel === 'undefined') {
        return ''
      }
      // Build an array of each adjs scores
      var adjs_scores = []
      for (var i = 0; i < this.panel.length; i++) {
        if (this.panel[i].position !== "T") {
          adjs_scores.push(allAdjudicators[this.panel[i].id].score);
        }
      }
      adjs_scores.sort(function(a,b){return b - a}) // Force numeric sort

      // Cull the scores from the presumed voting minority
      var majority = Math.ceil(adjs_scores.length / 2)
      adjs_scores = adjs_scores.slice(0, majority)
      var total = 0.0;
      for(var i = 0; i < adjs_scores.length; i++) {
          total = total + adjs_scores[i];
      }
      return (total / adjs_scores.length).toFixed(1);
    }
  }
}



</script>
