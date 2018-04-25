<template>
  <header class="db-margins-m db-flex-row h5 mb-2 mt-3">

    <div class="db-flex-item">

      {{ roundInfo.round }} {{ roundInfo.kind }} from {{ ballot.author }}
      <span v-if="roundInfo.votingBallots">
        ({{ authorPositionWithSoloCheck(ballot.authorPosition) }})
      </span>
      <span v-if="ballot.target">on {{ ballot.target }}
        <span v-if="ballot.targetPosition === 'c' || ballot.targetPosition === 'o'">(Chair)</span>
        <span v-if="ballot.targetPosition === 'p'">(Panellist)</span>
        <span v-if="ballot.targetPosition === 't'">(Trainee)</span>
      </span>

    </div>

    <div v-if="ballot.venue === '' || ballot.venue === null" class="ml-auto" >
      <span v-if="ballot.barcode">ID {{ ballot.barcode }}, </span>Venue:
      <span class="db-padding-horizontal db-fill-in"
            style="width: 232px; margin: 0 3px 0 5px; display: inline-block">
      </span>
    </div>

    <div v-else class="ml-auto ">
      <span v-if="ballot.barcode">ID {{ ballot.barcode }}, </span>
      {{ ballot.venue.display_name }}
    </div>

  </header>
</template>

<script>
import _ from 'lodash'


export default {
  props: ['ballot', 'roundInfo'],
  methods: {
    authorPositionWithSoloCheck: function (position) {
      if (position === 'c') {
        var panellists = _.filter(this.ballot.debateAdjudicators, function (da) {
          return da.position === 'p';
        })
        if (!_.isUndefined(panellists) && panellists.length > 0) {
          var voters = _.filter(this.ballot.debateAdjudicators, function (da) {
            return da.position !== 't';
          })
          return 'Chair for Panel of ' + voters.length
        }
        return 'Solo Chair'
      } else if (position === 'o') {
        return 'Solo Chair'
      } else if (position === 'p') {
        return 'Panellist'
      } else if (position === 't') {
        return 'Trainee'
      } else if (position === 'TEAM') {
        return 'Team'
      }
      return '?'
    },
  },
}
</script>
