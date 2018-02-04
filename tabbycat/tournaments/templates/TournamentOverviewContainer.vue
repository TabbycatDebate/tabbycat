<template>
  <div>

    <div class="row" v-if="graphData && graphData.length > 0">

      <div class="col">
        <div class="card mt-3">
          <div class="card-body">
            <h5 class="mb-0 text-center">Ballots Status</h5>
          </div>
          <ul class="list-group list-group-flush">
            <li class="list-group-item text-secondary">
              <ballots-graph :graph-data="graphData"></ballots-graph>
            </li>
          </ul>
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
            <updates-list v-for="action in actions" :key="action.id"
                          :item="action"></updates-list>
            <li class="list-group-item text-secondary" v-if="actions.length === 0">
              No Actions Yet
            </li>
          </ul>
        </div>
      </div>

      <div class="col mt-3">
        <div class="card">
          <div class="card-body">
            <h5 class="mb-0">Latest Results</h5>
          </div>
          <ul class="list-group list-group-flush">
            <updates-list v-for="ballot in ballots" :key="ballot.id"
                          :item="ballot"></updates-list>
            <li class="list-group-item text-secondary" v-if="ballots.length === 0">
              No Results Yet
            </li>
          </ul>
        </div>
      </div>

    </div>

  </div>
</template>

<script>
import UpdatesList from  '../../templates/graphs/UpdatesList.vue'
import BallotsGraph from '../../templates/graphs/BallotsGraph.vue'
import WebSocketMixin from '../../templates/ajax/WebSocketMixin.vue'
import _ from 'lodash'

export default {
  mixins: [ WebSocketMixin ],
  components: { UpdatesList, BallotsGraph },
  props: [ 'tournamentSlug', 'initialActions', 'initialBallots', 'initialGraphData'],
  data: function () {
    return {
      actions: this.initialActions,
      ballots: this.initialBallots,
      graphData: this.initialGraphData,
      socketPath: "actionlog"
    }
  },
  methods: {
    handleSocketMessage: function(stream, payload) {
      // Check what type the stream is

      if (stream === "actionlog") {
        var dataType = "actions"
      }
      if (stream === "ballot-results") {
        var dataType = "ballots"
      }
      if (stream === "ballot-statuses") {
        this.graphData = payload // pass to graph as prop
        return
      }

      // Check for duplicates; do a inline replace if so
      let duplicateIndex = _.findIndex(this[dataType], function(i) {
        return i.id == payload.id
      })

      if (duplicateIndex != -1) {
        this[dataType][duplicateIndex] = payload
      } else {
        // Add new item to front
        this[dataType].unshift(payload)
        // Remove last item if at the limit
        if (this[dataType].length >= 15) {
          this[dataType].pop()
        }
      }
    }
  }
}
</script>
