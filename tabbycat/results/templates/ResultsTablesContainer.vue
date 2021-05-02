<template>
  <div>

    <results-stats :checks="check_totals" :statuses="status_totals"></results-stats>

    <div class="row">
      <div class="col">
        <tables-container :tables-data="localTableData"></tables-container>
      </div>
    </div>

  </div>
</template>

<script>
import TablesContainer from '../../templates/tables/TablesContainer.vue'
import WebsocketMixin from '../../templates/ajax/WebSocketMixin.vue'
import ResultsStats from './ResultsStats.vue'

export default {
  mixins: [WebsocketMixin],
  components: { TablesContainer, ResultsStats },
  props: {
    tablesData: Array, tournamentSlug: String,
  },
  data: function () {
    return {
      localTableData: this.tablesData,
      sockets: ['ballot_statuses', 'checkins'],
    }
  },
  methods: {
    sumForType: function (objects, property, status) {
      const matches = objects.filter(o => o[property] === status)
      return matches.length
    },
    handleSocketReceive: function (socketLabel, payload) {
      const table = this.localTableData[0]
      if (socketLabel === 'ballot_statuses') {
        const row = table.data.find(cell => cell[1].id === payload.data.ballot.debate_id)
        if (!row) {
          return // Could not find matching debate; likely because its from another round
        }
        // Update ballot statuses
        row[1].status = payload.data.status
        row[1].icon = payload.data.icon
        row[1].class = payload.data.class
        row[1].sort = payload.data.sort
        // Update ballot links
        const payloadBallotId = payload.data.ballot.ballot_id
        const existingBallotIndex = row[2].ballots.findIndex(b => b.ballot_id === payloadBallotId)
        if (existingBallotIndex !== -1) {
          row[2].ballots[existingBallotIndex] = payload.data.ballot
        } else {
          row[2].ballots.push(payload.data.ballot)
        }
      }
      if (socketLabel === 'checkins' && payload.created) {
        // Note: must alter the original object not the computed property
        const identifier = payload.checkins[0].identifier
        if (!identifier) {
          return
        }
        const row = table.data.find(cell => cell[0].identifier === identifier)
        if (!row) {
          return // Could not find matching debate; likely because its from another round
        }
        row[0].check = 'checked'
        row[0].icon = 'check'
        row[0].class = 'text-secondary'
        row[0].sort = 1
      }
    },
  },
  computed: {
    tournamentSlugForWSPath: function () {
      return this.tournamentSlug
    },
    debates: function () {
      const rows = this.localTableData[0].data.map(cells => ({
        identifier: cells[0].identifier,
        id: cells[0].id,
        checked: cells[0].check,
        status: cells[1].status,
      }))
      return rows
    },
    check_totals: function () {
      return {
        checked: this.sumForType(this.debates, 'checked', 'checked'),
        missing: this.sumForType(this.debates, 'checked', 'missing'),
      }
    },
    status_totals: function () {
      return {
        none: this.sumForType(this.debates, 'status', 'N'),
        postponed: this.sumForType(this.debates, 'status', 'P'),
        draft: this.sumForType(this.debates, 'status', 'D'),
        confirmed: this.sumForType(this.debates, 'status', 'C'),
      }
    },
  },
}

</script>
