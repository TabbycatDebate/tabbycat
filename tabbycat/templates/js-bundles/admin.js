// Vue and the main app
var Vue = require('vue');
import vueBases from './main.js';

// Redefine so they can be edited
var vueComponents = vueBases.baseComponents;
var vueData = vueBases.baseData;
var vueMethods = null;
var vueCreated = null;

//------------------------------------------------------------------------------
// Tournament Homepage
//------------------------------------------------------------------------------

import UpdatesList from  '../js-vue/UpdatesList.vue'
import BallotsGraph from '../js-vue/graphs/BallotsGraph.vue'

if (typeof updateActionsURL !== 'undefined' && updateResultsURL !== null) {
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
// Main Vue Instance
//------------------------------------------------------------------------------

if (typeof bypassMainVue === 'undefined') {
  new Vue({
    el: 'body',
    components: vueComponents,
    data: vueData,
    methods: vueMethods,
    created: vueCreated
  });
}
