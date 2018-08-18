<template>
  <div>

    <results-stats :checks="checks" :statuses="statuses"></results-stats>

    <div class="row">
      <div class="col">
        <tables-container :tables-data="tablesData"></tables-container>
      </div>
    </div>

  </div>
</template>

<script>
import TablesContainer from '../../templates/tables/TablesContainer.vue'
import WebsocketMixin from  '../../templates/ajax/WebSocketMixin.vue'
import ResultsStats from './ResultsStats.vue'

export default {
  mixins: [WebsocketMixin],
  components: { TablesContainer, ResultsStats },
  props: { tablesData: Array },
  created: function () {
  },
  computed: {
    checks: function() {
      return {
        'checked': 9,
        'missing': 20
      }
    },
    statuses: function() {
      return {
        'none': 20,
        'draft': 21,
        'confirmed': 20
      }
    }
  },
  methods: {

  }
}

</script>