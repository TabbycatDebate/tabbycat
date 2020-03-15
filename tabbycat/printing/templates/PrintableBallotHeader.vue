<template>
  <header class="db-margins-m db-flex-row h5 mb-2 mt-3">

    <div class="db-flex-item">
      <span v-if="!roundInfo.votingBallots && !ballot.target"
            v-text="tct('%s from %s', [roundInfo.round, ballot.author])">
      </span>
      <span v-if="roundInfo.votingBallots"
            v-text="tct('%s from %s %s', [roundInfo.round, ballot.author, authorPositionWithSoloCheck(ballot.authorPosition)])">
      </span>
      <span v-if="ballot.target">
        <span v-if="ballot.targetPosition === 'c' || ballot.targetPosition === 'o'"
              v-text="tct('%s from %s on %s (Chair)', [roundInfo.round, ballot.author, ballot.target])"></span>
        <span v-if="ballot.targetPosition === 'p'"
              v-text="tct('%s from %s on %s (Panellist)', [roundInfo.round, ballot.author, ballot.target])"></span>
        <span v-if="ballot.targetPosition === 't'"
              v-text="tct('%s from %s on %s (Trainee)', [roundInfo.round, ballot.author, ballot.target])"></span>
        <span v-if="ballot.targetPosition === ''"
              v-text="tct('%s from %s on %s (unknown position)', [roundInfo.round, ballot.author, ballot.target])"></span>
      </span>

    </div>

    <div v-if="ballot.venue === '' || ballot.venue === null" class="ml-auto" >
      <span v-if="ballot.barcode"
            v-text="tct('ID %s,', [ballot.barcode])"></span>
      <span v-text="gettext('Room:')"></span>
      <span class="db-padding-horizontal db-fill-in"
            style="width: 232px; margin: 0 3px 0 5px; display: inline-block">
      </span>
    </div>

    <div v-else class="ml-auto ">
      <span v-if="ballot.barcode"
            v-text="tct('ID %s,', [ballot.barcode])"></span>
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
        const panellists = _.filter(this.ballot.debateAdjudicators, da => da.position === 'p')
        if (!_.isUndefined(panellists) && panellists.length > 0) {
          const voters = _.filter(this.ballot.debateAdjudicators, da => da.position !== 't')
          return this.tct('Chair for Panel of %s', [voters.length])
        }
        return this.gettext('Solo Chair')
      } else if (position === 'o') {
        return this.gettext('Solo Chair')
      } else if (position === 'p') {
        return this.gettext('Panellist')
      } else if (position === 't') {
        return this.gettext('Trainee')
      } else if (position === 'TEAM') {
        return this.gettext('Team')
      }
      return '?'
    },
  },
}
</script>
