<script>
import _ from 'lodash'

export default {
  data: function () {
    return {
      sharding: {
        enabled: false,
        splitNumeric: null,
        index: null,
        mix: null,
        sort: null,
      },
    }
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('open-shard', this.setShard)
  },
  computed: {
    debatesWithSharding: function () {
      var sortedDebates

      if (!this.sharding.enabled) {
        return this.debates
      }
      // Order debates by bracket
      sortedDebates = _.reverse(_.sortBy(this.debates, this.sharding.sort))
      // Re-order them to be evenly distributed single array if interleaved
      if (this.sharding.mix === 'interleave') {
        sortedDebates = this.sortInterleaved(sortedDebates, this.sharding.splitNumeric)
        console.log('interleaveShards', sortedDebates)
      }
      // Split up into sub arrays based on nominated shard size / index
      const shardedDebates = this.splitDebates(sortedDebates, this.sharding.splitNumeric)
      return shardedDebates[this.sharding.index]
    },
  },
  methods: {
    setShard: function (split, mix, sort, index) {
      if (split === 'Half') {
        this.sharding.splitNumeric = 2
      } else if (split === 'Third') {
        this.sharding.splitNumeric = 3
      } else if (split === 'Quarter') {
        this.sharding.splitNumeric = 4
      } else if (split === 'Fifth') {
        this.sharding.splitNumeric = 5
      }
      this.sharding.mix = mix
      this.sharding.sort = sort
      this.sharding.index = index
      this.sharding.enabled = true
      return null
    },
    splitDebates: function(debates, desiredSplit) {
      var splitDebates = []
      var n = desiredSplit
      var size = Math.floor(debates.length / n)
      var i = 0;

      // Sort debates into even chunks
      if (debates.length % n === 0) {
        while (i < debates.length) {
          splitDebates.push(debates.slice(i, i += size))
        }
      } else {
        n -= 1
        if (debates.length % size === 0) {
          size -= 1
        }
        while (i < size * n) {
          splitDebates.push(debates.slice(i, i += size))
        }
        splitDebates.push(debates.slice(size * n))
      }
      return splitDebates
    },
    sortInterleaved: function (debates, desiredSplit) {
      var interleavedDebates = []
      var j = 0;
      var i;

      // Make multidimensional array for each shard
      for (j = 0; j < desiredSplit; j += 1) {
        interleavedDebates[j] = []
      }

      // Split big array equally into shards; evenly distributing large-small
      j = 0
      for (i = 0; i < debates.length; i += 1) {
        interleavedDebates[j].push(debates[i])
        j += 1
        if (j >= desiredSplit) {
          j = 0
        }
      }
      return _.flatten(interleavedDebates)
    },
  },
}
</script>
