<template>
  <div>

    <div class="row">
      <div class="col-sm-12">
        <h4 class="text-center">Number of Ballots In</h4>
        <div class="panel panel-default">
          <div class="panel-body">
            <ballots-graph :poll-url="ballotsUrl"></ballots-graph>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-6">
        <h4 class="text-center">Latest Actions</h4>
        <ul class="list-group">
          <updates-list v-for="action in latestActions" :key="action.timestamp"
                        :item="action"></updates-list>
          <li class="list-group-item" v-if="!latestActions">Loading...</li>
          <li class="list-group-item" v-if="latestActions.length === 0">No Actions In</li>
        </ul>
      </div>
      <div class="col-md-6">
        <h4 class="text-center">Latest Results</h4>
        <ul class="list-group">
          <updates-list v-for="result in latestResults" :key="result.timestamp"
                        :item="result"></updates-list>
          <li class="list-group-item" v-if="!latestResults">Loading...</li>
          <li class="list-group-item" v-if="latestResults.length === 0">No Results In</li>
        </ul>
      </div>
    </div>

  </div>
</template>

<script>
import UpdatesList from  '../../graphs/UpdatesList.vue'
import BallotsGraph from '../../graphs/BallotsGraph.vue'

export default {
  mixins: [],
  components: { UpdatesList, BallotsGraph },
  props: [ 'actionsUrl', 'resultsUrl', 'ballotsUrl' ],
  data: function() {
    return {
      latestActions: false,
      latestResults: false,
      pollFrequency: 30000, // 30 seconds
    }
  },
  created: function() {
    this.updateActions()
    this.updateResults()
  },
  methods: {
      updateActions: function() {
        this.fetchData(this.actionsUrl, 'actions');
      },
      updateResults: function() {
        this.fetchData(this.resultsUrl, 'results');
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
}
</script>
