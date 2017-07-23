<template>
  <header class="db-margins-m db-flex-row db-flex-static db-flex-item-fhs">

    <div class="db-align-vertical-end db-flex-item-3">
      <h2>
        {{ roundInfo.round }} {{ roundInfo.tournamentName }} {{ roundInfo.kind }} from {{ ballot.author }}
        <span v-if="ballot.authorPosition === 'O'">(Solo Chair)</span>
        <span v-if="ballot.authorPosition === 'C'">(Chair of Panel)</span>
        <span v-if="ballot.authorPosition === 'P'">(Panellist)</span>
        <span v-if="ballot.authorPosition === 'T'">(Trainee)</span>
        <span v-if="ballot.target">on {{ ballot.target }}
          <span v-if="ballot.targetPosition === 'C' || ballot.targetPosition === 'o'">(Chair)</span>
          <span v-if="ballot.targetPosition === 'P'">(Panellist)</span>
          <span v-if="ballot.targetPosition === 'T'">(Trainee)</span>
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
    <div class="db-flex-static db-align-vertical-end" v-if="ballot.room !== ''">
      <h2>{{ ballot.room }}</h2>
    </div>

  </header>
</template>

<script>
export default {
  props: ['ballot', "roundInfo"],
}
</script>
