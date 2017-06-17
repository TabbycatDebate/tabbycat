<template>
  <header class="db-margins-m db-flex-row db-flex-static db-flex-item-fhs">

    <div class="db-align-vertical-end db-flex-item-3">
      <h2>
        {{ roundInfo.tournamentName }} {{ roundInfo.kind }} from {{ ballot.author }}
        <span v-if="ballot.authorPosition === 'o'">(Solo Chair)</span>
        <span v-if="ballot.authorPosition === 'c'">(Chair of Panel)</span>
        <span v-if="ballot.authorPosition === 'p'">(Panellist)</span>
        <span v-if="ballot.authorPosition === 't'">(Trainee)</span>
        <span v-if="ballot.target">on {{ ballot.target }}
          <span v-if="ballot.targetPosition === 'c' || ballot.targetPosition === 'o'">(Chair)</span>
          <span v-if="ballot.targetPosition === 'p'">(Panellist)</span>
          <span v-if="ballot.targetPosition === 't'">(Trainee)</span>
        </span>
      </h2>
    </div>
    <template v-if="ballot.room === ''">
      <div class="db-flex-static db-align-vertical-end">
        <h2>Venue:</h2>
        <span class="db-padding-horizontal db-fill-in"
              style="width: 125px; margin: 0 15px 0 5px; display: inline-block">
        </span>
      </div>
    </template>
    <div class="db-flex-static db-align-vertical-end">
      <h2>
        <span v-if="ballot.room !== ''">{{ ballot.room }}</span>
        {{ roundInfo.round }}
      </h2>
    </div>

  </header>
</template>

<script>
export default {
  props: ['ballot', "roundInfo"],
}
</script>
