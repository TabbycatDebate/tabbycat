<template>
  <div class="row flex-horizontal">

    <div class="flex-cell flex-vertical-center bordered-bottom">
      <div class="flex-1 text-center" data-toggle="tooltip" title="Debate is in the {{ debate.bracket }} bracket">
        {{ debate.bracket }}
      </div>
    </div>

    <div class="flex-cell flex-vertical-center bordered-bottom">
      <div class="flex-1 text-center" data-toggle="tooltip" title="{{ liveness }} teams are live">
        {{ liveness }}
      </div>
    </div>

    <div class="flex-cell importance-container flex-vertical-center bordered-bottom">
      <div class="flex-1">
        <debate-importance
          :id="debate.id"
          :importance="debate.importance"
          :url="this.roundInfo['updateImportanceURL']">
        </debate-importance>
      </div>
    </div>

    <debate-team :adjorteam="aff"></debate-team>

    <debate-team :adjorteam="neg"></debate-team>

    <div class="flex-6">
      <div class="panel panel-default panel-debate">
        <div class="flex-horizontal positions-parent">
          <div class="flex-cell flex-vertical-center bordered-bottom">
            <div class="flex-1" data-toggle="tooltip" title="{{ panelScore }} is the average rating of this panel's voting majority">
              {{ panelScore }}
            </div>
          </div>
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


  </div>
</template>

<script>
import AjaxMixin from '../mixins/AjaxMixin.vue'
import DebateTeam from './DebateTeam.vue'
import DebateImportance from './DebateImportance.vue'
import PositionDroppable from './PositionDroppable.vue'
import ConflictsCalculatorMixin from '../mixins/ConflictsCalculatorMixin.vue'

export default {
  components: {
    DebateTeam, DebateImportance, PositionDroppable
  },
  mixins: [
    AjaxMixin, ConflictsCalculatorMixin
  ],
  props: {
    allAdjudicators: Object,
    debate: Object,
    aff: Object,
    neg: Object,
    roundInfo: Object
  },
  computed: {
    debateAdjudicators: function () {
      // Find the panel array set from JSON
      var panel = this.debate.panel;
      var debateAdjudicators = {
        chair: [],
        panelists: [],
        trainees: []
      }
      // Loop through it and match up the adjudicators by ID
      for (var i = 0; i < panel.length; ++i) {
        var foundAdj = this.allAdjudicators[panel[i].id]
        if (panel[i].position === "C" || panel[i].position === "O") {
          debateAdjudicators.chair.push(foundAdj);
        } else if (panel[i].position === "P") {
          debateAdjudicators.panelists.push(foundAdj);
         } else if (panel[i].position === "T") {
          debateAdjudicators.trainees.push(foundAdj);
        }
      }
      return debateAdjudicators;
    },
    liveness: function() {
      var liveness = 0;
      for (var i = 0; i < this.aff.categories.length; ++i) {
        if (this.aff.categories[i].will_break === null) {
          liveness += 1;
        }
      }
      for (var i = 0; i < this.neg.categories.length; ++i) {
        if (this.neg.categories[i].will_break === null) {
          liveness += 1;
        }
      }
      return liveness;
    },
    panelScore: function () {
      var panel = this.debate.panel;
      if (typeof panel === 'undefined' || panel.length === 0) {
        return ''
      }
      // Build an array of each adjs scores
      var adjs_scores = []
      for (var i = 0; i < panel.length; i++) {
        if (panel[i].position !== "T") {
          adjs_scores.push(Number(allAdjudicators[panel[i].id].score));
        }
      }
      if (adjs_scores.length === 0) {
        return ''
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
    },
    conflictableTeams: function() {
      var teams = {}
      teams[this.aff.id] = this.aff
      teams[this.neg.id] = this.neg
      return teams
    },
    conflictableAdjudicators: function() {
      var adjudicators = {}
      for(var i = 0; i < this.debateAdjudicators.chair.length; i++) {
        var adjudicator = this.debateAdjudicators.chair[i]
        adjudicators[adjudicator.id] = adjudicator
      }
      for(var i = 0; i < this.debateAdjudicators.panelists.length; i++) {
        var adjudicator = this.debateAdjudicators.panelists[i]
        adjudicators[adjudicator.id] = adjudicator
      }
      for(var i = 0; i < this.debateAdjudicators.trainees.length; i++) {
        var adjudicator = this.debateAdjudicators.trainees[i]
        adjudicators[adjudicator.id] = adjudicator
      }
      return adjudicators
    },
  },
  events: {
    'recheck-panel-conflicts': function() {
      this.checkPanelConflicts(true, this.conflictableTeams, this.conflictableAdjudicators)
    },
  },
  methods: {
    checkPanelConflicts: function(conflictValue, conflictableTeams, conflictableAdjudicators) {
      this.unsetAll('panel', conflictableTeams)
      this.unsetAll('panel', conflictableAdjudicators)
      for (var teamID in conflictableTeams) {
        if (conflictableTeams.hasOwnProperty(teamID)) {
          var team = conflictableTeams[teamID];
          this.toggleConflicts(conflictValue, 'panel', team, team.conflicts);
          this.toggleHistories(conflictValue, 'panel', team, team.histories);
        }
      }
      for (var adjID in conflictableAdjudicators) {
        if (conflictableAdjudicators.hasOwnProperty(adjID)) {
          var adj = conflictableAdjudicators[adjID];
          this.toggleConflicts(conflictValue, 'panel', adj, adj.conflicts);
          this.toggleHistories(conflictValue, 'panel', team, adj.histories);
        }
      }
    }
  },
  created: function() {
    // Do initial calculation for conflicts/histories
    this.checkPanelConflicts(true, this.conflictableTeams, this.conflictableAdjudicators)
  },
  watch: {
    'debate.panel': function (newVal, oldVal) {
      // Make AJAX request to save new panel composition
      var resource = "change to panel on  " + this.aff.name + " vs " + this.neg.name
      var data = {
        'debate_id': this.debate.id,
        'panel': JSON.stringify(this.debate.panel)
      }
      this.update(this.roundInfo['updatePanelURL'], data, resource);
    },
    'conflictableAdjudicators': function (newVal, oldVal) {
      this.checkPanelConflicts(true, this.conflictableTeams, newVal)
    }
  }
}



</script>
