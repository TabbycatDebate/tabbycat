<template>
  <checkbox-tables-container  :tables-data="localTableData"
                              :categories="categories"
                              :round-info="roundInfo"
                              :translations="translations"
                              :urls="urls"
                              :navigation="navigation"
                              :hide-auto-save="hideAutoSave" >
  </checkbox-tables-container>
</template>

<script>
import CheckboxTablesContainer from '../../templates/tables/TablesContainer.vue'
import WebsocketMixin from '../../templates/ajax/WebSocketMixin.vue'

export default {
  mixins: [WebsocketMixin],
  components: { CheckboxTablesContainer },
  props: {
    tablesData: Array,
    categories: Array,
    urls: Object,
    navigation: Array,
    roundInfo: Object,
    translations: Object,
    hideAutoSave: Boolean,
    tournamentSlug: String,
    speakers: String,
  },
  data: function () {
    return {
      localTableData: this.tablesData,
      substantiveSpeakers: Number(this.speakers),
      sockets: ['checkins'],
    }
  },
  methods: {
    handleSocketReceive: function (socketLabel, payload) {
      const table = this.localTableData[0]
      const col = table.headers[1].key === 'active-prev' ? 2 : 1
      if (socketLabel === 'checkins') {
        // Note: must alter the original object not the computed property
        for (const checkin of payload.checkins) {
          if (!checkin.identifier) {
            continue
          }
          const row = table.data.find(cell => cell[col].identifiers.find(id => id.identifier === identifier))
          if (!row) {
            continue // Could not find matching participant; probably different type
          }
          const identifier = row[col].identifiers.find(id => id.identifier === identifier)
          identifier.checked = payload.status

          if (this.roundInfo.model === 'participants.Team') {
            const numChecked = row[col].identifiers.reduce((sum, id) => sum + (id.checked ? 1 : 0), 0)
            if (numChecked >= this.substantiveSpeakers - 1) {
              row[col].sort = numChecked >= this.substantiveSpeakers - 1
              row[col].icon = numChecked >= this.substantiveSpeakers ? 'check' : 'shuffle'
            } else {
              row[col].sort = false
              row[col].icon = ''
            }
          } else {
            row[col].sort = identifier.checked
            row[col].icon = identifier.checked ? 'check' : ''
          }

          row[0].checked_in = row[col].sort
        }
      }
    },
  },
  computed: {
    tournamentSlugForWSPath: function () {
      return this.tournamentSlug
    },
  },
}

</script>
