<template>

  <div class="modal fade" :id="id" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4">

          <p class="lead" v-text="introText"></p>
          <p v-text="gettext(explanationText)"></p>
          <p v-text="gettext(splitExplanation)"></p>

          <div class="btn-group mb-4 btn-group-toggle" role="group">
            <button v-text="gettext('Shard Mix')" class="btn btn-outline-secondary"></button>
            <button v-for="option in mixOptions" type="button" @click="setState('mix', option)"
                    :class="['btn btn-outline-primary', mix === option ? 'active': '']"
                    v-text="gettext(option)"></button>
          </div>

          <div class="btn-group mb-4 btn-group-toggle" role="group">
            <button v-text="gettext('Shard Split')" class="btn btn-outline-secondary"></button>
            <button v-for="option in splitOptions" type="button" @click="setState('split', option)"
                    :class="['btn btn-outline-primary', split === option ? 'active': '']"
                    v-text="gettext('In ' + option)"></button>
          </div>

          <div class="btn-group mb-4 btn-group-toggle" role="group">
            <button v-text="gettext('Shard Sort')" class="btn btn-outline-secondary"></button>
            <button v-for="option in sortOptions" type="button" @click="setState('sort', option)"
                    :class="['btn btn-outline-primary', sort === option ? 'active': '']"
                    v-text="gettext('By ' + option)"></button>
          </div>

          <div class="btn-group d-block" role="group">
            <button v-if="!split || !sort || !mix" class="btn btn-secondary disabled"
                    v-text="gettext('Select a count, sort, and mix to open a shard')"></button>
            <button v-else type="button" class="btn btn-success" @click="openShard(shard, index)"
                    v-for="(shard, index) in shardOptions"
                    v-text="gettext('Open') + ' ' + gettext(split) + ' ' + shard"></button>
          </div>

        </div>
      </div>
    </div>
  </div>

</template>

<script>
export default {
  props: { introText: String },
  data: function () {
    // Internal state storing the status of which diversity highlight is being toggled
    return {
      splitOptions: ['Halves', 'Thirds', 'Quarters', 'Fifths'],
      split: null,
      mixOptions: ['Top-to-Bottom', 'Interleaved'],
      mix: null,
      sortOptions: ['Bracket', 'Priority', 'Liveness'],
      sort: null,
      explanationText: `This helps allow this page to be edited across several computers as it
        guarantees that changes made in one shard wont affect the others. However, you need to
        ensure that each computer uses identical split/mix/sort settings and selects a different
        shard from the others`,
      splitExplanation: `Top-to-Bottom mixing will sort the draw so the first shard contains the
        top-most brackets, priority, or liveness while the last shard contains the bottom-most
        brackets, priority, or liveness. In contrast, Interleave will distribute an even mix of each
        characteristic amongst each shard`,
      id: 'confirmShardModal',
    }
  },
  computed: {
    shardOptions: function () {
      if (this.split === 'Halves') {
        return ['A', 'B']
      } else if (this.split === 'Thirds') {
        return ['A', 'B', 'C']
      } else if (this.split === 'Quarters') {
        return ['A', 'B', 'C', 'D']
      } else if (this.split === 'Fifths') {
        return ['A', 'B', 'C', 'D', 'E']
      }
      return null
    },
  },
  methods: {
    resetModal: function () {
      $(this.id).modal('hide')
    },
    openShard: function (shardIdentifier, index) {
      $.fn.showAlert('primary', `Opened shard ${this.split} ${shardIdentifier}
                                 (sorted by ${this.mix} using ${this.sort})`)
    },
    setState: function (type, state) {
      this[type] = state
    },
  },
}
</script>
