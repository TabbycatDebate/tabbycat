<template>
  <div class="row">

    <div class="col-md-1">
      <debate-importance
        :id="debate.id"
        :importance="debate.importance"
        :url="debate.importance_url">
      </debate-importance>
    </div>

    <div class="col-md-1">
      {{ debate.bracket }}
    </div>

    <div class="col-md-1">
      <debate-team :team="aff"></debate-team>
    </div>

    <div class="col-md-1">
      <debate-team :team="neg"></debate-team>
    </div>

    <div class="col-md-8">
      <div class="panel panel-default">
        <div class="flex-horizontal positions-parent">

          <position-droppable
            :adjudicators="debateAdjudicators.chair"
            :position="C">
          </position-droppable>
          <position-droppable
            :adjudicators="debateAdjudicators.panelists"
            :position="P">
          </position-droppable>
          <position-droppable
            :adjudicators="debateAdjudicators.trainees"
            :position="T">
          </position-droppable>

        </div>
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
    }
  }
}



</script>
