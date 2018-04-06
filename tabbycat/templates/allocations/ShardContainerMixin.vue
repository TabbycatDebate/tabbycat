<script>
import _ from 'lodash'

export default {
  data: function () {
    return {
      sharding: false,
      splitNumeric: null,
      index: null,
      sort: null,
    }
  },
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('open-shard', this.setShard)
  },
  computed: {
    debatesWithSharding: function () {
      var sortedDebates

      if (!this.sharding) {
        return this.debates
      }
      // Order debates by bracket
      sortedDebates = _.reverse(_.sortBy(this.debates, ['bracket', 'liveness']))

      // Re-order them to be evenly distributed single array if interleaved
      if (this.sort === 'interleave') {
        sortedDebates = this.splitDebates(sortedDebates, this.splitNumeric)
        sortedDebates = this.interleaveShards(sortedDebates)
      }

      const shardedDebates = this.splitDebates(sortedDebates, this.splitNumeric)
      console.log('shardedDebates', shardedDebates)
      return shardedDebates[this.index]
    },
  },
  methods: {
    setShard: function (split, sort, index) {
      if (split === 'Half') {
        this.splitNumeric = 2
      } else if (split === 'Third') {
        this.splitNumeric = 3
      } else if (split === 'Quarter') {
        this.splitNumeric = 4
      } else if (split === 'Fifth') {
        this.splitNumeric = 5
      }
      this.sort = sort
      this.index = index
      this.sharding = true
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
    interleaveShards: function (shards) {
      var interleavedDebates = []
      var i;

      console.log('shards', shards)
      const shardLengths = shards.map((shard) => shard.length)
      const maxLength = _.max(shardLengths)
      console.log('maxLength', maxLength)

      for (i = 0; i < maxLength; i += 1) {
        shards.forEach((shardArray) => {
          if (shardArray.length > i) {
            interleavedDebates.push(shardArray[i])
          }
        })
      }
      console.log('interleavedDebates', interleavedDebates)

      return interleavedDebates
    },
  },
}
</script>
