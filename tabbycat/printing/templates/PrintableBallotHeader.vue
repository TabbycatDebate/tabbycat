<template>
  <header class="db-margins-m db-flex-row db-flex-static db-flex-item-fhs">

    <div class="db-align-vertical-end db-flex-item-3">
      <h2>
        {{ roundInfo.round }} {{ roundInfo.kind }} from {{ ballot.author }}
        <span v-if="roundInfo.votingBallots">
          ({{ authorPositionWithSoloCheck(ballot.authorPosition) }})
        </span>
        <span v-if="ballot.target">on {{ ballot.target }}
          <span v-if="ballot.targetPosition === 'c' || ballot.targetPosition === 'o'">(Chair)</span>
          <span v-if="ballot.targetPosition === 'p'">(Panellist)</span>
          <span v-if="ballot.targetPosition === 't'">(Trainee)</span>
        </span>
      </h2>
    </div>
    <template v-if="ballot.venue === '' || ballot.venue === null">
      <div class="db-flex-static db-align-vertical-end">
        <h2>Venue:</h2>
        <span class="db-padding-horizontal db-fill-in"
              style="width: 185px; margin: 0 3px 0 5px; display: inline-block">
        </span>
      </div>
    </template>
    <div v-else class="db-flex-static db-align-vertical-end">
      <h2>{{ ballot.venue.display_name }}</h2>
    </div>

  </header>
</template>

<script>
import _ from 'lodash'

export default {
  props: ['ballot', "roundInfo"],
  methods: {
    authorPositionWithSoloCheck: function(position) {
      if (position === 'c') {
        var panellists = _.filter(this.ballot.debateAdjudicators, function(da) {
          return da.position === "p";
        })
        if (!_.isUndefined(panellists) && panellists.length > 0) {
          var voters = _.filter(this.ballot.debateAdjudicators, function(da) {
            return da.position !== "t";
          })
          return "Chair for Panel of " + voters.length
        } else {
          return "Solo Chair"
        }
      } else if (position === 'o') {
        return "Solo Chair"
      } else if (position === 'p') {
        return "Panellist"
      } else if (position === 't') {
        return "Trainee"
      } else if (position === 'TEAM') {
        return "Team"
      } else {
        return "?"
      }
    }
  }
}
</script>
