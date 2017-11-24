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
    autoAssignImportance: function(assignedType) {
      var debatesByType = _.sortBy(this.debates, assignedType)
      var length = debatesByType.length

      // Assign quartile bounds
      var quartile1Index = Math.floor(length * 0.25) - 1
      var quartile1Upper = Math.ceil(debatesByType[quartile1Index][assignedType])
      var quartile2Index = Math.floor(length * 0.50) - 1
      var quartile2Upper = Math.ceil(debatesByType[quartile2Index][assignedType])
      var quartile3Index = Math.floor(length * 0.75) - 1
      var quartile3Upper = Math.ceil(debatesByType[quartile3Index][assignedType])
      var quartile4Upper = debatesByType[length - 1][assignedType] + 1
      var q = [{ 'start': 0,              'end': quartile1Upper},
               { 'start': quartile1Upper, 'end': quartile2Upper},
               { 'start': quartile2Upper, 'end': quartile3Upper},
               { 'start': quartile3Upper, 'end': quartile4Upper}]

      // Sometimes brackets can start and end at the same number which creates
      // skewed distributions (no debates in that 1/4); this helps compensate
      var increaser = 0
      for (var i = 0; i < 4; i += 1) {
        q[i]['start'] = q[i]['start'] + increaser
        q[i]['end'] = q[i]['end'] + increaser
        if (q[i]['start'] === q[i]['end']) {
          increaser += 1
          q[i]['end'] += increaser
        }
      }

      console.log(assignedType, q)

      // Actually assign the importances
      for (var j = 0; j < this.debates.length; j += 1) {
        var debate = this.debates[j]
        if (_.inRange(debate[assignedType], q[0].start, q[0].end)) {
          debate.importance = -2
        } else if (_.inRange(debate[assignedType], q[1].start, q[1].end)) {
          debate.importance = -1
        } else if (_.inRange(debate[assignedType], q[2].start, q[2].end)) {
          debate.importance = 0
        } else if (_.inRange(debate[assignedType], q[3].start, q[3].end)) {
          debate.importance = 1
        }
      }

      // Save the results
      var debateIDs = _.map(this.debates, 'id')
      var debateImportances = _.map(this.debates, 'importance')
      this.updateImportance(debateIDs, debateImportances)
    },
    updateImportance: function(debateIDs, importances) {
      var payload = { 'priorities': {}}
      for (var i = 0; i < debateIDs.length; i += 1) {
        payload['priorities'][debateIDs[i]] = importances[i]
      }
      var url = this.roundInfo.updateImportanceURL
      var message = 'debate IDs ' + debateIDs + '\'s importance'
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
