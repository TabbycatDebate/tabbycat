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

          </ul>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import UpdatesList from  '../../templates/graphs/UpdatesList.vue'
import BallotsGraph from '../../templates/graphs/BallotsGraph.vue'
import { WebSocketBridge } from 'django-channels'

export default {
  mixins: [],
  components: { UpdatesList, BallotsGraph },
  props: [ 'initialActions', 'ballotsUrl', 'roundStatus'],
  data: function () {
    return {
      actions: this.initialActions
    }
  },
  created: function() {
    // Subscribe to action log web stocket stream
    var sock = new WebSocket("ws://" + window.location.host + "/actionlog/latest/");
    sock.onmessage = function (event) {
      this.updateActions(JSON.parse(event.data).payload.data)
    }
  },
  methods: {
    updateActions: function(data) {
      this.actions.pop() // Remove last item
      this.actions.unshift(data) // Add new item to front
    }
  }
}
</script>
