<template>
  <header class="db-margins-m db-flex-row db-flex-static db-flex-item-fhs">

    <div class="db-align-vertical-end db-flex-item-3">
      <h2>
        {{ roundInfo.round }} {{ roundInfo.kind }} from {{ ballot.author }}
        ({{ authorPositionWithSoloCheck(ballot.authorPosition) }})
        <span v-if="ballot.target">on {{ ballot.target }}
          <span v-if="ballot.targetPosition === 'C' || ballot.targetPosition === 'o'">(Chair)</span>
          <span v-if="ballot.targetPosition === 'P'">(Panellist)</span>
          <span v-if="ballot.targetPosition === 'T'">(Trainee)</span>
        </span>
      </h2>
    </div>
    <template v-if="ballot.venue === '' || ballot.venue === null">
      <div class="db-flex-static db-align-vertical-end">
        <h2>Venue:</h2>
        <span class="db-padding-horizontal db-fill-in"
              style="width: 200px; margin: 0 3px 0 5px; display: inline-block">
        </span>
      </div>
    </template>
    <div v-else class="db-flex-static db-align-vertical-end">
      <h2>{{ ballot.venue.name }}</h2>
    </div>

  </header>
</template>

<script>
import _ from 'lodash'

export default {
  props: ['ballot', "roundInfo"],
  methods: {
    authorPositionWithSoloCheck: function(position) {
      if (position === 'C') {
        var panellists = _.filter(this.ballot.debateAdjudicators, function(da) {
          return da.position === "P";
        })
        if (!_.isUndefined(panellists) && panellists.length > 0) {
          return "Chair of Panel"
        } else {
          return "Solo Chair"
        }
      } else if (position === 'O') {
        return "Solo Chair"
      } else if (position === 'P') {
        return "Panellist"
      } else if (position === 'T') {
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
