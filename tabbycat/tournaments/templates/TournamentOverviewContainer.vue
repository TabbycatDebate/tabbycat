<template>
  <div>

    <div class="row" v-if="roundStatus === 'R' || roundStatus === 'C'">

      <div class="col">
        <div class="card mt-3">
          <div class="card-body">
            <h5 class="mb-2 text-center">Ballots Status</h5>
            <!-- <ballots-graph :poll-url="ballotsUrl"></ballots-graph> -->
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
  props: [ 'initialActions', 'initialBallots', 'roundStatus'],
  data: function () {
    return {
      actions: this.initialActions,
      ballots: this.initialBallots,
      socketPath: "/actionlog/latest/"
    }
  },
  methods: {
    handleSocketMessage: function(message) {
      // Check what type the stream is
      if (message.model === "actionlog.actionlogentry") {
        var dataType = "actions"
      }
      if (message.model === "results.ballotsubmission") {
        var dataType = "ballots"
        console.log('handle ballot', message.data.confirmed)
        if (message.data.confirmed === false) {
          return // Don't update the list for unconfirmed ballots
        }
      }
      // Check for duplicates; do a inline replace if so
      let duplicateIndex = _.findIndex(this[dataType], function(i) {
        return i.id == message.data.id
      })
      if (duplicateIndex != -1) {
        this[dataType][duplicateIndex] = message.data
        console.log('duplicate')
      } else {
        this[dataType].pop() // Remove last item
        this[dataType].unshift(message.data) // Add new item to front
        console.log('add')
      }
    }
  }
}
</script>
