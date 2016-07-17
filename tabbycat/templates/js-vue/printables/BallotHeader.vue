<template>

  <header class="db-margins-m db-flex-row db-flex-item-1">

    <div class="db-align-vertical-end db-flex-item-3">
      <h2>
        {{ data.tournamentName }} {{ data.kind }} from {{ ballot.author }}
        <span v-if="soloChair">(Solo Chair)</span>
        <span v-if="panelChair">(Chair of Panel)</span>
        <span v-if="ballot.authorPosition === 'P'">(Panellist)</span>
        <span v-if="ballot.authorPosition === 'T'">(Trainee)</span>
        <span v-if="ballot.target">on {{ ballot.target }}
          <span v-if="ballot.targetPosition === 'C'">(Chair)</span>
          <span v-if="ballot.targetPosition === 'P'">(Panellist)</span>
          <span v-if="ballot.targetPosition === 'T'">(Trainee)</span>
        </span>
      </h2>
    </div>
    <div class="db-flex-static db-align-vertical-end">
      <h2>{{ ballot.room }} {{ data.round }}</h2>
    </div>

  </header>

</template>

<script>
export default {
  props: ['data', 'ballot'],
  computed: {
    soloChair: function() {
      if (this.ballot.authorPosition === 'C') {
        var voting_adjs = 0;
        this.ballot.panel.forEach(function(entry) {
          if (entry.position !== "T") { voting_adjs++; };
        }, this);
        if (voting_adjs === 1) { return true }
      }
      return false
    },
    panelChair: function() {
      if (this.ballot.authorPosition === 'C') {
        var voting_adjs = 0;
        this.ballot.panel.forEach(function(entry) {
          if (entry.position !== "T") { voting_adjs++; };
        }, this);
        if (voting_adjs > 1) { return true }
      }
      return false
    }
  }
}
</script>
