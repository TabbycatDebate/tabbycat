<template>
  <div class="modal fade" id="confirmShardingModal" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p class="lead">Sharding will narrow the debates shown here to show a specific subset of the overall draw.</p>
          <p>When using sharding to allow multiple people to allocate simultaneously <strong>be very sure</strong> that everyone is using the same <em>count</em>, <em>split</em>, and the each person has selected a different shard from the others.</p>
          <p><em>Top-to-Bottom</em> splitting will sort the draw so the first shard contains debates from the top-most brackets, and the last shard contains debates from the bottom-most brackets.</p>
          <p><em>Interleave</em> splitting will distribute an even mix of brackets amongst each of the shards</p>
          <div class="text-center">
            <h4>Shard Count</h4>
            <div class="btn-group mb-3 btn-group-toggle" role="group">
              <button type="button" @click="setState('split', 'Half')"
                      :class="['btn btn-primary', split === 'Half' ? 'active': '']">
                  Halves
              </button>
              <button type="button" @click="setState('split', 'Third')"
                      :class="['btn btn-primary', split === 'Third' ? 'active': '']">
                  Thirds
              </button>
              <button type="button" @click="setState('split', 'Quarter')"
                      :class="['btn btn-primary', split === 'Quarter' ? 'active': '']">
                  Quarters
              </button>
              <button type="button" @click="setState('split', 'Fifth')"
                      :class="['btn btn-primary', split === 'Fifth' ? 'active': '']">
                  Fifths
              </button>
            </div>
          </div>
          <div class="text-center mt-3">
            <h4>Shard Split</h4>
            <div class="btn-group mb-3 btn-group-toggle" role="group">
              <button type="button" @click="setState('sort', 'hierarchy')"
                      :class="['btn btn-primary', sort === 'hierarchy' ? 'active': '']">
                Top-to-Bottom
              </button>
              <button type="button" @click="setState('sort', 'interleave')"
                      :class="['btn btn-primary', sort === 'interleave' ? 'active': '']">
                Interleaved
              </button>
            </div>
          </div>
          <div class="text-center mt-3 mb03">
            <h4>Select Shard</h4>
            <button v-if="split === null || sort === null" class="btn btn-secondary disabled">
              Select a count and split to open a particular shard
            </button>
            <div v-else class="btn-group mb-3" role="group">
              <button type="button" class="btn btn-success"
                      @click="openShard(split, sort, shardIdentifier, index)"
                      v-for="(shardIdentifier, index) in shardOptions">
                {{ split }} {{ shardIdentifier }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: { roundInfo: Object },
  data: function () {
    // Internal state storing the status of which diversity highlight is being toggled
    return {
      split: null,
      sort: null,
    }
  },
  computed: {
    shardOptions: function () {
      if (this.split === 'Half') {
        return ['A', 'B']
      } else if (this.split === 'Third') {
        return ['A', 'B', 'C']
      } else if (this.split === 'Quarter') {
        return ['A', 'B', 'C', 'D']
      } else if (this.split === 'Fifth') {
        return ['A', 'B', 'C', 'D', 'E']
      }
      return null
    },
  },
  methods: {
    resetShardingModal: function (button) {
      $('#confirmShardingModal').modal('hide')
      $.fn.resetButton('#shpb')
      $.fn.resetButton('#shpl')
    },
    openShard: function (split, sort, shardIdentifier, index) {
      var self = this
      $.fn.loadButton('#shpb')
      $.fn.loadButton('#shpl')
      self.$eventHub.$emit('open-shard', split, sort, index)

      $.fn.showAlert('success', `Opened shard ${split} ${shardIdentifier} (sorted by ${sort})`,  10000)
      self.resetShardingModal()
    },
    setState: function (type, state) {
      this[type] = state;
    },
  },
}

</script>
