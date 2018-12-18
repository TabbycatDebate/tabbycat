<template>

  <div class="card pr-0 mr-0 m-2">
    <div class="list-group list-group-flush">

      <div class="list-group-item pb-0">
        <div class="row">
          <!-- team-name class used by unknown sides switcher -->
          <div class="col mr-auto card-title pl-md-2 pl-1" v-html="team.name"></div>
          <div class="col-auto card-subtitle text-muted text-right pt-2 pr-md-2 pr-1">
            <h6>{{ team.position }}</h6>
          </div>
        </div>
      </div>

      <ballot-entry-speaker v-for="(speaker, index) in team.speakers"
                            v-on:update-speaker-score="calculateTeamPoints"
                            :speaker="speaker" :index="index" :key="index"
                            :show-duplicates="showDuplicates"></ballot-entry-speaker>

      <div class="list-group-item">
        <div class="row">

          <div class="col-2 p-lg-2 pr-0 p-1"></div>

          <div class="col mb-0 pr-md-1 pr-1 btn-group d-flex">
            <button tabindex="-1" class="btn w-100 btn-outline-secondary btn-no-hover" readonly>Rank</button>
            <button tabindex="-1" :class="['btn w-100 btn-no-hover text-monospace border-right-0 ', rankClasses[teamRank]]" readonly>
              {{ rankLabels[teamRank] }}
            </button>
            <button tabindex="-1" class="btn w-100 btn-outline-secondary btn-no-hover" readonly>Margin</button>
            <button tabindex="-1" :class="['btn w-100 btn-no-hover text-monospace', rankClasses[teamRank]]" readonly>
              <span v-if="teamMargin >= 0">+</span>{{ teamMargin }}
            </button>
          </div>

          <div class="col-3 btn-group pr-md-2 pr-1">
            <button tabindex="-1" :class="['btn btn-block btn-no-hover', rankClasses[teamRank]]" readonly>
              {{ teamPoints }}
            </button>
          </div>

        </div>
      </div>

    </div>
  </div>

</template>

<script>
import BallotEntrySpeaker from './BallotEntrySpeaker.vue'

export default {
  components: { BallotEntrySpeaker },
  props: { team: Object, teamScores: Object, teamsCount: Number, showDuplicates: Boolean },
  data: function () {
    return {
      speakerScores: [],
      rankLabels: {
        1: '1st',
        2: '2nd',
        3: '3rd',
        4: '4th',
        '?': '?',
        'tie': 'TIE',
      },
      rankClasses: {
        1: 'btn-success',
        2: 'btn-info',
        3: 'btn-warning',
        4: 'btn-danger',
        '?': 'btn-secondary',
        'tie': 'btn-dark',
      },
    }
  },
  computed: {
    teamPoints: function () {
      return this.teamScores[this.team.position]
    },
    teamMargin: function () {
      let nonZeroScores = Object.values(this.teamScores).filter(s => s > 0)
      if (nonZeroScores.length !== this.teamsCount) { return '?   ' }
      return this.teamScores[this.team.position] - Object.values(this.teamScores).sort().slice(-1)
    },
    teamRank: function () {
      let nonZeroScores = Object.values(this.teamScores).filter(s => s > 0)
      if (nonZeroScores.length !== this.teamsCount) { return '?' }
      let scores = Object.values(this.teamScores).sort().reverse()
      for (const [index, score] of scores.entries()) {
        if (score === this.teamScores[this.team.position]) {
          if (Object.values(this.teamScores).filter(s => s === score).length > 1) {
            return 'tie'
          }
          return index + 1
        }
      }
      return '?'
    },
  },
  methods: {
    calculateTeamPoints: function (index, score) {
      if (typeof this.speakerScores[index] === 'undefined') {
        this.speakerScores.push(score)
      } else {
        this.speakerScores[index] = score
      }
      let totalSpeaks = this.speakerScores.reduce((a, b) => a + b, 0) // Can't call from computed
      this.$emit('update-team-score', this.team.position, totalSpeaks)
    },
  },
}
</script>
