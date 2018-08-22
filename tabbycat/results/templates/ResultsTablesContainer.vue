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
  props: { tablesData: Array, 'tournamentSlug': String },
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
        // Going to have to reconstruct both the status icon for this debate
        // But also the edit links
        var row = this.localTableData[0].data.find(function (cell) {
          return cell[1].id === payload.data.debate_id
        })
        row[1].status = payload.data.status
        row[1].icon = payload.data.icon
        row[1].class = payload.data.class
      }
      if (socketLabel === 'checkins' && payload.created) {
        // Note: must alter the original object not the computed property
        var row = this.localTableData[0].data.find(function (cell) {
          return cell[0].identifier === payload.checkins[0].identifier
        })
        row[0].check = 'checked'
        row[0].icon = 'check'
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