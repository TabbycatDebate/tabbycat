<script setup>
import _ from 'lodash'

import { computed, defineAsyncComponent, ref, toRef } from 'vue'
import UpdatesList from '../../templates/graphs/UpdatesList.vue'
import { useWebSocket } from '../../templates/composables/useWebSocket.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

const BallotsGraph = defineAsyncComponent(() => import('../../templates/graphs/BallotsGraph.vue'))

const props = defineProps({
  tournamentSlug: String,
  totalDebates: Number,
  initialActions: Array,
  initialBallots: Array,
  initialGraphData: Array,
  permissions: Object,
})

const { gettext } = useDjangoI18n()

const actionLogs = ref(props.initialActions)
const ballotResults = ref(props.initialBallots)
const ballotStatuses = ref(props.initialGraphData)

const tournamentSlugForWSPath = toRef(props, 'tournamentSlug')

const sockets = computed(() => {
  const s = []
  if (props.permissions.actionlog) {
    s.push('action_logs')
  }
  if (props.permissions.graph) {
    s.push('ballot_statuses')
  }
  if (props.permissions.results) {
    s.push('ballot_results')
  }
  return s
})

const handleSocketReceive = (socketLabel, payload) => {
  const data = payload.data
  if (socketLabel === 'ballot_statuses') {
    ballotStatuses.value.push(data)
    return
  }
  const target = (socketLabel === 'ballot_results') ? ballotResults : actionLogs
  if (socketLabel === 'ballot_results') {
    if (data.confirmed === false || data.result_status !== 'C') {
      return
    }
  }
  const duplicateIndex = _.findIndex(target.value, i => i.id === data.id)
  if (duplicateIndex !== -1) {
    target.value[duplicateIndex] = data
  } else {
    target.value.unshift(data)
    if (target.value.length >= 15) {
      target.value.pop()
    }
  }
}

useWebSocket({
  sockets: sockets.value,
  tournamentSlugForWSPath,
  handleSocketReceive,
})
</script>

<template>
  <div>
    <div
      v-if="totalDebates > 0"
      class="row"
    >
      <div class="col">
        <div class="card mt-3">
          <div class="card-body">
            <h5 class="mb-0 text-center">
              {{ gettext('Ballots Status') }}
            </h5>
          </div>
          <ul class="list-group list-group-flush">
            <li
              v-if="permissions.graph"
              class="list-group-item text-secondary px-2"
            >
              <ballots-graph
                :graph-data="ballotStatuses"
                :total-debates="totalDebates"
              />
            </li>
            <li
              v-else
              class="list-group-item text-secondary text-center"
            >
              {{ gettext('No Results Yet') }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col mt-3">
        <div class="card">
          <div class="card-body">
            <h5 class="mb-0">
              {{ gettext('Latest Actions') }}
            </h5>
          </div>
          <ul
            v-if="permissions.actionlog"
            class="list-group list-group-flush"
          >
            <updates-list
              v-for="action in actionLogs"
              :key="action.id"
              :item="action"
            />
          </ul>
          <ul
            v-else
            class="list-group list-group-flush"
          >
            <li class="list-group-item text-secondary">
              {{ gettext('No Actions Yet') }}
            </li>
          </ul>
        </div>
      </div>

      <div class="col mt-3">
        <div class="card">
          <div class="card-body">
            <h5 class="mb-0">
              {{ gettext('Latest Results') }}
            </h5>
          </div>
          <ul
            v-if="permissions.results"
            class="list-group list-group-flush"
          >
            <updates-list
              v-for="ballot in ballotResults"
              :key="ballot.id"
              :item="ballot"
            />
          </ul>
          <ul
            v-else
            class="list-group list-group-flush"
          >
            <li class="list-group-item text-secondary">
              {{ gettext('No Confirmed Results Yet') }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
