// Libraries
var Vue = require('vue')

// Components
var UpdatesList = require('../js-vue/UpdatesList.vue')
var BallotsGraph = require('../js-vue/graphs/BallotsGraph.vue')

new Vue({
  el: '#tournamentOverview',
  components: {
    UpdatesList, BallotsGraph
  },
  data: {
    latestActions: 'loading',
    latestResults: 'loading',
    pollFrequency: 30000, // 30 seconds
  },
  created: function () {
    this.updateActions();
    this.updateResults();
  },
  methods: {
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
          self.latestActions = JSON.parse(xhr.responseText);
          setTimeout(self.updateActions, self.pollFrequency);
        } else {
          self.latestResults = JSON.parse(xhr.responseText);
          setTimeout(self.updateResults, self.pollFrequency);
        }
      }
      xhr.send()
    }
  }
})