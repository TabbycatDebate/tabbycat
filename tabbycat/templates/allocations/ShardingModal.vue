<template>
  <div class="modal fade" id="confirmShardingModal" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center">

          <p class="lead">
            Sharding will narrow the debates displayed to show a specific subset
            of the overall draw.
          </p>
          <p class="lead">
            This feature is in beta — be sure to double check the main draw page for missing or
            duplicated adjudicators.
          </p>
          <p>
            When using sharding to allow multiple people to allocate simultaneously
            <strong>be very sure</strong> that everyone is using the same <em>split</em>,
            <em>sort</em>, <em>mix</em>, and that each person has selected a different
            shard from the others.
          </p>

          <h4>Shard Split</h4>
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

          <h4 class="mt-3">Shard Sort</h4>
          <div class="btn-group mb-3 btn-group-toggle" role="group">
            <button type="button" @click="setState('sort', 'bracket')"
                    :class="['btn btn-primary', sort === 'bracket' ? 'active': '']">
              By Bracket
            </button>
            <button type="button" @click="setState('sort', 'importance')"
                    :class="['btn btn-primary', sort === 'importance' ? 'active': '']">
              By Priority
            </button>
            <button type="button" @click="setState('sort', 'liveness')"
                    :class="['btn btn-primary', sort === 'liveness' ? 'active': '']">
              By Liveness
            </button>
          </div>

          <h4 class="mt-3">Shard Mix</h4>
          <p>
            <em>Top-to-Bottom</em> mixing will sort the draw so the first shard contains debates
            from the top-most brackets, priority, or liveness, and the last shard contains debates
            from the bottom-most brackets, priority, orliveness. <em>Interleave</em> mixing will
            distribute an even mix of each characteristic amongst each of the shards
          </p>
          <div class="btn-group mb-3 btn-group-toggle" role="group">
            <button type="button" @click="setState('mix', 'hierarchy')"
                    :class="['btn btn-primary', mix === 'hierarchy' ? 'active': '']">
              Top-to-Bottom
            </button>
            <button type="button" @click="setState('mix', 'interleave')"
                    :class="['btn btn-primary', mix === 'interleave' ? 'active': '']">
              Interleaved
            </button>
          </div>

          <h4 class="mt-3">Select Shard</h4>
          <button v-if="split === null || sort === null || mix === null"
                  class="btn btn-secondary disabled">
            Select a count, sort, and mix to open a shard
          </button>
          <div v-else class="btn-group" role="group">
            <button type="button" class="btn btn-success"
                    @click="openShard(shardIdentifier, index)"
                    v-for="(shardIdentifier, index) in shardOptions">
              {{ split }} {{ shardIdentifier }}
            </button>
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
      mix: null,
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
    resetShardingModal: function () {
      $('#confirmShardingModal').modal('hide')
      $.fn.resetButton('#shpb')
      $.fn.resetButton('#shpl')
    },
    openShard: function (shardIdentifier, index) {
      const self = this
      $.fn.loadButton('#shpb')
      $.fn.loadButton('#shpl')
      self.$eventHub.$emit('open-shard', this.split, this.mix, this.sort, index)

      $.fn.showAlert('primary', `Opened shard ${this.split} ${shardIdentifier}
                                 (sorted by ${this.mix} using ${this.sort})`)
      self.resetShardingModal()
    },
    setState: function (type, state) {
      this[type] = state
    },
  },
}

</script>
