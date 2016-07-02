// Vue and the main app
var Vue = require('vue');
import vueBases from './main.js';

// Redefine so they can be edited
var vueComponents = vueBases.baseComponents;
var vueData = vueBases.baseData;
var vueMethods = null, vueCreated = null, vueFilters = null, vueEvents = null;

//------------------------------------------------------------------------------
// Adj Allocation
//------------------------------------------------------------------------------

import AllocationContainer from '../js-vue/allocations/AllocationContainer.vue'

if (typeof allAdjudicators !== 'undefined' && allAdjudicators !== null) {
  // All vue data table views must provide this base tablesData in the template
  vueComponents['AllocationContainer'] = AllocationContainer;
  vueData['allDebates'] = allDebates;
  vueData['allAdjudicators'] = allAdjudicators;
  vueData['allTeams'] = allTeams;
  vueData['allRegions'] = allRegions;
  vueData['allCategories'] = allCategories;
  vueData['urls'] = urls;
}

//------------------------------------------------------------------------------
// Tournament Homepage
//------------------------------------------------------------------------------

import UpdatesList from  '../js-vue/UpdatesList.vue'
import BallotsGraph from '../js-vue/graphs/BallotsGraph.vue'

if (typeof updateActionsURL !== 'undefined' && updateResultsURL !== 'undefined') {
  vueComponents['UpdatesList'] = UpdatesList;
  vueComponents['BallotsGraph'] = BallotsGraph;
  vueData = {
      latestActions: 'loading',
      latestResults: 'loading',
      pollFrequency: 30000, // 30 seconds
      updateActionsURL: updateActionsURL, // From template
      updateResultsURL: updateResultsURL, // From template
  };
  vueMethods = {
    updateActions: function() {
      this.fetchData(updateActionsURL, 'actions')
    },
    updateResults: function() {
      this.fetchData(updateResultsURL, 'results')
    },
    fetchData: function (apiURL, resource) {
      var xhr = new XMLHttpRequest()
      var self = this
      xhr.open('GET', apiURL)
      xhr.onload = function () {
        if (resource === 'actions') {
          self.latestActions = JSON.parse(xhr.responseText)
          setTimeout(self.updateActions, self.pollFrequency)
        } else {
          self.latestResults = JSON.parse(xhr.responseText)
          setTimeout(self.updateResults, self.pollFrequency)
        }
      }
      xhr.send()
    }
  };
  vueCreated = function () {
    this.updateActions()
    this.updateResults()
  };
}

//------------------------------------------------------------------------------
// Printables
//------------------------------------------------------------------------------

import Ballot from  '../js-vue/printables/Ballot.vue'

if (typeof printableBaseData !== 'undefined' && printableBaseData !== null) {
  vueData = printableBaseData; // From Template
  vueComponents['Ballot'] = Ballot;
}

//------------------------------------------------------------------------------
// Divisons Allocator
//------------------------------------------------------------------------------

import DivisionDroppable from  '../js-vue/draganddrops/DivisionDroppable.vue'
import TeamDraggable from  '../js-vue/draganddrops/TeamDraggable.vue'

if (typeof divisionsBaseData !== 'undefined' && divisionsBaseData !== null) {
  vueData = divisionsBaseData; // From Template
  vueMethods = divisionsMethods; // From Template
  vueEvents = divisionsEvents; // From Template
  vueFilters = divisionsFilters; // From Template
  vueComponents['DivisionDroppable'] = DivisionDroppable;
  vueComponents['TeamDraggable'] = TeamDraggable;
}

//------------------------------------------------------------------------------
// Main Vue Instance
//------------------------------------------------------------------------------

if (typeof bypassMainVue === 'undefined') {
  new Vue({
    el: 'body',
    components: vueComponents,
    created: vueCreated,
    data: vueData,
    events: vueEvents,
    filters: vueFilters,
    methods: vueMethods
  });
}
