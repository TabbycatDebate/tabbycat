<script>
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams
  created: function() {
    this.$eventHub.$on('update-importance', this.updateImportance)
    this.$eventHub.$on('assign-all-importances', this.autoAssignImportance)
  },
  methods: {
    autoAssignImportance: function(type) {
      if (type === 'bracket') {
        this.autoAssignImportanceByBracket()
      }
      if (type === 'liveness') {
        this.autoAssignImportanceByLiveness()
      }
    },
    autoAssignImportanceByBracket: function() {
      var debatesByBracket = _.sortBy(this.debates, 'bracket')
      // For the highest/lowest bracket we actually take the third-highest and
      // third lowest bracket to even out the uneven distribution of brackets
      var fakeHighestBracket = debatesByBracket[debatesByBracket.length - 3]
      var highestBracket = fakeHighestBracket.bracket
      var fakeLowestBracket = debatesByBracket[2]
      var lowestBracket = fakeLowestBracket.bracket

      // 15 difference; (20/5); quartile is thus 4
      var bracketQuartilesSpan = (highestBracket - lowestBracket) / 4

      console.log(lowestBracket, highestBracket, 'span', bracketQuartilesSpan)
      for (var i = 0; i < 4; i += 1) {

        if (i == 0) {
          var bracketLowerThreshold = 0 // Ensure lowest quartile includes edges
        } else {
          var bracketLowerThreshold = lowestBracket + (bracketQuartilesSpan * i)
        }
        if (i == 3) {
          var bracketUpperThreshold = 99 // Ensure top quartile includes edges
        } else {
          var bracketUpperThreshold = lowestBracket + (bracketQuartilesSpan * i) + bracketQuartilesSpan
        }

        console.log(bracketLowerThreshold, bracketUpperThreshold)

        for (var j = 0; j < this.debates.length; j += 1) {
          if ((this.debates[j].bracket < bracketUpperThreshold) &&
              (this.debates[j].bracket >= bracketLowerThreshold)) {
            this.debates[j].importance = i - 2
            // console.log('bracket', this.debates[j].bracket, bracketUpperThreshold, bracketLowerThreshold, "quartile", i)
          }

        }
      }

    },
    autoAssignImportanceByLiveness: function() {

    },
    updateImportance: function(debateID, importance) {
      var debate = _.find(this.debates, { 'id': debateID })
      if (_.isUndefined(debate)) {
        this.ajaxError("Debate\'s importance", "", "Couldnt find debate to update")
      }
      var url = this.roundInfo.updateImportanceURL
      var message = 'debate ' + debate.id + '\'s importance'
      var payload = { 'priorities': {}}
      payload['priorities'][debate.id] = importance
      this.ajaxSave(url, payload, message, this.processImportanceSaveSuccess, null, null)
    },
    processImportanceSaveSuccess: function(dataResponse, payload, returnPayload) {
      var self = this
      _.forEach(dataResponse, function(importance, debateID) {
        self.debatesById[parseInt(debateID)]['importance'] = importance
      });
    }
  },
}
</script>
