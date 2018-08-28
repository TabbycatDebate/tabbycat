<script>
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams
  created: function () {
    this.$eventHub.$on('update-importance', this.updateImportance)
    this.$eventHub.$on('assign-importance-by-liveness', this.autoAssignImportanceByLiveness)
    this.$eventHub.$on('assign-importance-by-bracket', this.autoAssignImportanceByBracket)
  },
  methods: {
    autoAssignImportanceByLiveness: function () {
      for (let i = 0; i < this.debates.length; i += 1) {
        const debate = this.debates[i]
        if (debate.nliveteams > 0) {
          debate.importance = 1 // some teams live
        } else if (debate.nsafeteams > 0) {
          debate.importance = 0 // all teams safe
        } else {
          debate.importance = -2// all teams dead
        }
      }
      const debateIDs = _.map(this.debates, 'id')
      const debateImportances = _.map(this.debates, 'importance')
      this.updateImportance(debateIDs, debateImportances)
    },
    autoAssignImportanceByBracket: function () {
      const counts = _.countBy(this.debates, 'bracket')
      const brackets = []
      let cumfreq = 0

      _.forOwn(counts, (count, bracket) => {
        cumfreq += count
        brackets.push({ points: _.parseInt(bracket), count: count, cumfreq: cumfreq })
      })

      const targetSize = this.debates.length / 4
      let thresholds = []
      for (let i = 1; i < 4; i += 1) {
        const boundary = _.minBy(brackets, (bracket) => {
          const diff = bracket.cumfreq - (i * targetSize)
          // bias towards lower side, if two are equidistant
          return Math.abs(diff) + ((diff > 0) ? 0.1 : 0)
        })
        thresholds.push(boundary.points)
      }
      thresholds = _.uniq(thresholds)

      const grouped = _.groupBy(this.debates, (debate) => {
        for (let j = 0; j < thresholds.length; j += 1) {
          if (debate.bracket <= thresholds[j]) {
            return j - (thresholds.length + 1)
          }
        }
        return 1
      })

      _.forOwn(grouped, (debates, importance) => {
        debates.forEach((debate) => {
          debate.importance = _.parseInt(importance)
        })
      })

      const debateIDs = _.map(this.debates, 'id')
      const debateImportances = _.map(this.debates, 'importance')
      this.updateImportance(debateIDs, debateImportances)
    },
    updateImportance: function (debateIDs, importances) {
      const payload = { priorities: {} }
      for (let i = 0; i < debateIDs.length; i += 1) {
        payload.priorities[debateIDs[i]] = importances[i]
      }
      const url = this.roundInfo.updateImportanceURL
      const message = `debate IDs ${debateIDs}'s importance`
      this.ajaxSave(url, payload, message, this.processImportanceSaveSuccess, null, null)
    },
    processImportanceSaveSuccess: function (dataResponse) {
      const self = this
      _.forEach(dataResponse, (importance, debateID) => {
        self.debatesById[parseInt(debateID)].importance = importance
      })
    },
  },
}
</script>
