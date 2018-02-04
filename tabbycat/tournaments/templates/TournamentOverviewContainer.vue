<template>
  <div>

    <div class="row" v-if="ballot_statuses && ballot_statuses.length > 0">

      <div class="col">
        <div class="card mt-3">
          <div class="card-body">
            <h5 class="mb-0 text-center">Ballots Status</h5>
          </div>
          <ul class="list-group list-group-flush">
            <li class="list-group-item text-secondary">
              <ballots-graph :graph-data="ballot_statuses"></ballots-graph>
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
            <updates-list v-for="action in actionlogs" :key="action.id"
                          :item="action"></updates-list>
            <li class="list-group-item text-secondary" v-if="actionlogs.length === 0">
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
            <updates-list v-for="ballot in ballot_results" :key="ballot.id"
                          :item="ballot"></updates-list>
            <li class="list-group-item text-secondary" v-if="ballot_results.length === 0">
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
      actionlogs: this.initialActions,
      ballot_results: this.initialBallots,
      ballot_statuses: this.initialGraphData,
      sockets: ['actionlogs', 'ballot_results', 'ballot_statuses']
    }
  },
  methods: {
    handleSocketMessage: function(payload, socketLabel) {
      console.log('handleSocketMessage', socketLabel, ' : ', payload)
      if (socketLabel === 'ballot_statuses') {
        this.ballot_statuses = payload
        return
      }
      // Check for duplicates; do a inline replace if so
      let duplicateIndex = _.findIndex(this[socketLabel], function(i) {
        return i.id == payload.id
      })
      if (duplicateIndex != -1) {
        this[socketLabel][duplicateIndex] = payload
      } else {
        // Add new item to front
        this[socketLabel].unshift(payload)
        // Remove last item if at the limit
        if (this[socketLabel].length >= 15) {
          this[socketLabel].pop()
        }
      }
    }
  }
}
</script>
