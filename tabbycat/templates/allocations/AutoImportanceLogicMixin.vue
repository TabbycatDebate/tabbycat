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
    autoAssignImportanceByLiveness: function() {
      for (var i = 0; i < this.debates.length; i += 1) {
        var debate = this.debates[i]
        if (debate.nliveteams > 0)
          debate.importance = 1    // some teams live
        else if (debate.nsafeteams > 0)
          debate.importance = 0    // all teams safe
        else
          debate.importance = -2   // all teams dead
      }
      var debateIDs = _.map(this.debates, 'id')
      var debateImportances = _.map(this.debates, 'importance')
      this.updateImportance(debateIDs, debateImportances)
    },
    autoAssignImportanceByBracket: function() {
      var counts = _.countBy(this.debates, 'bracket')
      var brackets = []
      var cumfreq = 0

      _.forOwn(counts, function (count, bracket) {
        cumfreq += count
        brackets.push({points: _.parseInt(bracket), count: count, cumfreq: cumfreq})
      })

      var targetSize = this.debates.length / 4
      var thresholds = []
      for (var i = 1; i < 4; i += 1) {
        var boundary = _.minBy(brackets, function(bracket) {
          var diff = bracket.cumfreq - i * targetSize
          return Math.abs(diff) + ((diff > 0) ? 0.1 : 0)  // bias towards lower side, if two are equidistant
        })
        thresholds.push(boundary.points)
      }
      thresholds = _.uniq(thresholds)

      var grouped = _.groupBy(this.debates, function (debate) {
        for (var j = 0; j < thresholds.length; j += 1)
          if (debate.bracket <= thresholds[j])
            return j - thresholds.length + 1;
        return 1;
      })

      _.forOwn(grouped, function (debates, importance) {
        for (var debate of debates) {
          debate.importance = _.parseInt(importance)
        }
      })

      var debateIDs = _.map(this.debates, 'id')
      var debateImportances = _.map(this.debates, 'importance')
      this.updateImportance(debateIDs, debateImportances)
    },
    updateImportance: function (debateIDs, importances) {
      var payload = { 'priorities': {}}
      for (var i = 0; i < debateIDs.length; i += 1) {
        payload['priorities'][debateIDs[i]] = importances[i]
      }
      var url = this.roundInfo.updateImportanceURL
      var message = 'debate IDs ' + debateIDs + '\'s importance'
      this.ajaxSave(url, payload, message, this.processImportanceSaveSuccess, null, null)
    },
    processImportanceSaveSuccess: function (dataResponse, payload, returnPayload) {
      var self = this
      _.forEach(dataResponse, function (importance, debateID) {
        self.debatesById[parseInt(debateID)]['importance'] = importance
      });
    }
  },
}
</script>
