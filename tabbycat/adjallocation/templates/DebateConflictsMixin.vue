<script>
import ConflictsCoordinatorMixin from '../allocations/ConflictsCoordinatorMixin.vue'
import _ from 'lodash'

export default {
  // Designed to be applied to a Debate component or in the EditAdjudicatorsContainer
  // It relies on both components having a conflicts/histories dictionary;
  // which in the case of a Debate only lists the adjudicators present
  // This the same logic can be used to check for conflicts/histories

  mixins: [ConflictsCoordinatorMixin],
  computed: {
    panel: function() {
      return this.debate.panel
    },
    teamsById: function() {
      return _.keyBy(this.debate.teams, 'id')
    },
    adjudicatorsById: function() {
      var adjudicators = _.map(this.debate.panel, function(panellist) {
        return panellist.adjudicator
      })
      return _.keyBy(adjudicators, 'id')
    }
  },
  mounted: function () {
    this.checkForPanelClashes()
  },
  methods: {
    checkForPanelClashes() {
      var self = this
      if (self.debate.id === 131) {
      // REDUX;


      //   _.forEach(this.panel, function(panellist) {
      //     // Get all the conflicts for a given pannellist from the inherited debate-relevant list
      //     var panellistId = panellist.adjudicator.id

      //     // Get the full list of conflicts they have; need to remove reactivity as we filter it
      //     var panellistsConflicts = _.cloneDeep(self.conflicts[panellistId])

      //     // Filter these out so they only include IDs present in the debate
      //     panellistsConflicts.adjudicator = _.remove(panellistsConflicts.adjudicator, function(conflictsId) {
      //       // We check if the conflicting adj ID is on this debate
      //       return _.includes(_.keys(self.adjudicatorsById), conflictsId.toString());
      //     });
      //     panellistsConflicts.team = _.remove(panellistsConflicts.team, function(conflictsId) {
      //       // We check if the conflicting adj ID is on this debate
      //       return _.includes(_.keys(self.teamsById), conflictsId.toString());
      //     });
      //     panellistsConflicts.institution = []
      //     console.log(panellist.adjudicator.name, panellistsConflicts)

      //     // Get the full list of histories they have
      //     var panellistsHistories = [] // self.histories[panellistId]

      //     // Check their thing
      //     self.$eventHub.$emit('set-conflicts-for', panellist.adjudicator,
      //                          panellistsConflicts, panellistsHistories, true, 'panel')
      //   })
      }
    }
  },
  watch: {
    panel: function(panel) {
      this.checkForPanelClashes()
    },
  }
}
</script>
