<script setup>
import { computed, ref, toRef } from 'vue'
import TablesContainer from '../../templates/tables/TablesContainer.vue'
import { useWebSocket } from '../../templates/composables/useWebSocket.js'
import ResultsStats from './ResultsStats.vue'

const props = defineProps({
  tablesData: Array,
  tournamentSlug: String,
})

const localTableData = ref(props.tablesData)

const sockets = ['ballot_statuses', 'checkins']
const tournamentSlugForWSPath = toRef(props, 'tournamentSlug')

const sumForType = (objects, property, status) => {
  const matches = objects.filter(o => o[property] === status)
  return matches.length
}

const handleSocketReceive = (socketLabel, payload) => {
  const table = localTableData.value[0]
  if (socketLabel === 'ballot_statuses') {
    const row = table.data.find(cell => cell[1].id === payload.data.ballot.debate_id)
    if (!row) {
      return
    }
    row[1].status = payload.data.status
    row[1].icon = payload.data.icon
    row[1].class = payload.data.class
    row[1].sort = payload.data.sort

    const payloadBallotId = payload.data.ballot.ballot_id
    const existingBallotIndex = row[2].ballots.findIndex(b => b.ballot_id === payloadBallotId)
    if (existingBallotIndex !== -1) {
      row[2].ballots[existingBallotIndex] = payload.data.ballot
    } else {
      row[2].ballots.push(payload.data.ballot)
    }
  }
  if (socketLabel === 'checkins' && payload.created) {
    const identifier = payload.checkins[0].identifier
    if (!identifier) {
      return
    }
    const row = table.data.find(cell => cell[0].identifier === identifier)
    if (!row) {
      return
    }
    row[0].check = 'checked'
    row[0].icon = 'check'
    row[0].class = 'text-secondary'
    row[0].sort = 1
  }
}

useWebSocket({
  sockets,
  tournamentSlugForWSPath,
  handleSocketReceive,
})

const debates = computed(() => {
  return localTableData.value[0].data.map(cells => ({
    identifier: cells[0].identifier,
    id: cells[0].id,
    checked: cells[0].check,
    status: cells[1].status,
  }))
})

const check_totals = computed(() => {
  return {
    checked: sumForType(debates.value, 'checked', 'checked'),
    missing: sumForType(debates.value, 'checked', 'missing'),
  }
})

const status_totals = computed(() => {
  return {
    none: sumForType(debates.value, 'status', 'N'),
    postponed: sumForType(debates.value, 'status', 'P'),
    draft: sumForType(debates.value, 'status', 'D'),
    confirmed: sumForType(debates.value, 'status', 'C'),
  }
})
</script>

<template>
  <div>
    <results-stats
      :checks="check_totals"
      :statuses="status_totals"
    />

    <div class="row">
      <div class="col">
        <tables-container :tables-data="localTableData" />
      </div>
    </div>
  </div>
</template>
