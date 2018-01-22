<template>
  <div>

    <div class="row" v-if="graphData && graphData.length > 0">

      <div class="col">
        <div class="card mt-3">
          <div class="card-body">
            <h5 class="mb-2 text-center">Ballots Status</h5>
            <ballots-graph :graph-data="graphData" :poll-url="ballotsUrl"></ballots-graph>
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
  props: [ 'tournamentId', 'initialActions', 'initialBallots', 'initialGraphData'],
  data: function () {
    return {
      actions: this.initialActions,
      ballots: this.initialBallots,
      graphData: this.initialGraphData,
      socketPath: "actionlog/overviews"
    }
  },
  methods: {
    handleSocketMessage: function(stream, payload) {
      // Check what type the stream is

      if (stream === "status") {
        this.graphData = payload
        return
      }
      if (stream === "actionlog") {
        var dataType = "actions"
      }
      if (stream === "ballot") {
        var dataType = "ballots"
        if (payload.confirmed === false) {
          return // Don't update the list for unconfirmed ballots
        }
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
