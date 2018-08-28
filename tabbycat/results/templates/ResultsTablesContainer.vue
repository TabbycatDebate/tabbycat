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
    tablesData: Array, 'tournamentSlug': String
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
      if (socketLabel === 'ballot_statuses') {
        var row = this.localTableData[0].data.find(function (cell) {
          return cell[1].id === payload.data.ballot.debate_id
        })
        // Update ballot statuses
        row[1].status = payload.data.status
        row[1].icon = payload.data.icon
        row[1].class = payload.data.class
        row[1].sort = payload.data.sort
        // Update ballot links
        const existingBallotIndex = row[2].ballots.findIndex(function(ballot) {
          return ballot.ballot_id === payload.data.ballot.ballot_id;
        });
        if (existingBallotIndex != -1) {
          row[2].ballots[existingBallotIndex] = payload.data.ballot
        } else {
          row[2].ballots.push(payload.data.ballot)
        }
      }
      if (socketLabel === 'checkins' && payload.created) {
        // Note: must alter the original object not the computed property
        var row = this.localTableData[0].data.find(function (cell) {
          return cell[0].identifier === payload.checkins[0].identifier
        })
        row[0].check = 'checked'
        row[0].icon = 'check'
        row[0].class = 'text-secondary'
        row[0].sort = 1
      }
    }
  },
  computed: {
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
        draft: this.sumForType(this.debates, 'status', 'D'),
        confirmed: this.sumForType(this.debates, 'status', 'C'),
      }
    },
  },
}

</script>