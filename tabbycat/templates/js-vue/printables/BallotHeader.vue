<template>

  <header class="db-margins-m db-flex-row db-flex-item-1">

    <div class="db-align-vertical-end db-flex-item-3">
      <h2>
        {{ data.tournamentName }} {{ data.kind }} from {{ ballot.author }}
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
    <div class="db-flex-static db-align-vertical-end">
      <h2>{{ ballot.room }} {{ data.round }}</h2>
    </div>

  </header>

</template>

<script>
export default {
  props: ['data', 'ballot'],
}
</script>
