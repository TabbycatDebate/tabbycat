<template>
  <div>

    <div class="row" v-if="roundStatus === 'R' || roundStatus === 'C'">

      <div class="col">
        <div class="card mt-3">
          <div class="card-body">
            <h5 class="mb-2 text-center">Ballots Status</h5>
            <ballots-graph :poll-url="ballotsUrl"></ballots-graph>
          </div>
        </div>
      </div>

    </div>

    <div class="row">

      <div class="col mt-3">
        <div class="card">
          <div class="card-body">
            <h5 class="mb-0">Latest Actions</h5>
          </div>
          <ul class="list-group list-group-flush">
            <updates-list v-for="action in latestActions" :key="action.timestamp"
                          :item="action"></updates-list>
            <li class="list-group-item text-secondary" v-if="!latestActions">Loading...</li>
            <li class="list-group-item text-secondary" v-if="latestActions.length === 0">No Actions Yet</li>
          </ul>
        </div>
      </div>

      <div class="col mt-3">
        <div class="card">
          <div class="card-body">
            <h5 class="mb-0">Latest Results</h5>
          </div>
          <ul class="list-group list-group-flush">
            <updates-list v-for="result in latestResults" :key="result.timestamp"
                          :item="result"></updates-list>
            <li class="list-group-item text-secondary" v-if="!latestResults">Loading...</li>
            <li class="list-group-item text-secondary" v-if="latestResults.length === 0">No Results Yet</li>
          </ul>
        </div>
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
  props: [ 'actionsUrl', 'resultsUrl', 'ballotsUrl', 'roundStatus'],
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
        console.log('DEBUG: JSON TournamentOverview fetchData onload:', xhr.responseText)
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
