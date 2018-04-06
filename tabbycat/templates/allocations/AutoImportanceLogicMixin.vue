<script>
import _ from 'lodash'

export default {
  // Designed to be applied to a Panel component as a bridge between
  // acting across the entire adj/team pool (for hovers) and instead only
  // focusing it on conflicts within a debate panel / debate teams
  created: function () {
    this.$eventHub.$on('update-importance', this.updateImportance)
    this.$eventHub.$on('assign-all-importances', this.autoAssignImportance)
  },
  methods: {
    autoAssignImportance: function (assignedType) {
      var debatesByType = _.sortBy(this.debates, assignedType)
      var length = debatesByType.length
      var chunkLimits = [0] // Floor value for start of lowest chunk

      // Assign proportions; account for cases where too few debates for 1/3rds
      if (length <= 2) {
        chunkLimits.push(debatesByType[1][assignedType])
      } else if (length === 3) {
        chunkLimits.push(debatesByType[1][assignedType], debatesByType[2][assignedType])
      } else {
        // Determine the values that define the upper and lower limit of each span
        var chunks = [0.25, 0.5, 0.75]
        for (var i = 0; i < chunks.length; i += 1) {
          var splitIndex = Math.floor(length * chunks[i]) - 1
          var splitThreshold = Math.ceil(debatesByType[splitIndex][assignedType])
          chunkLimits.push(splitThreshold) // Brackets can be at 0; but already
        }
      }
      chunkLimits.push(debatesByType[length - 1][assignedType] + 1) // ceiling

      // Create a dictionary of upper/lower limits for each span used to group
      var chunkSpans = []
      for (var i = 0; i < chunkLimits.length - 1; i += 1) {
        chunkSpans.push({ 'start': chunkLimits[i], 'end': chunkLimits[i + 1] })
      }

      // Sometimes brackets can start and end at the same number which creates
      // skewed distributions (no debates in that 1/4); this helps compensate
      var increaser = 0
      for (var i = 0; i < chunkSpans.length; i += 1) {
        chunkSpans[i]['start'] = chunkSpans[i]['start'] + increaser
        chunkSpans[i]['end'] = chunkSpans[i]['end'] + increaser
        if (chunkSpans[i]['start'] === chunkSpans[i]['end']) {
          increaser += 1
          chunkSpans[i]['end'] += increaser
        }
      }

      // Actually assign the importances
      for (var j = 0; j < this.debates.length; j += 1) {
        var debate = this.debates[j]
        if (_.inRange(debate[assignedType], chunkSpans[0].start, chunkSpans[0].end)) {
          debate.importance = -2
        } else if (_.inRange(debate[assignedType], chunkSpans[1].start, chunkSpans[1].end)) {
          debate.importance = -1
        } else if (_.inRange(debate[assignedType], chunkSpans[2].start, chunkSpans[2].end)) {
          debate.importance = 0
        } else if (_.inRange(debate[assignedType], chunkSpans[3].start, chunkSpans[3].end)) {
          debate.importance = 1
        }
      }

      // Save the results
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
