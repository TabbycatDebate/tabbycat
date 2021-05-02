<template>

  <div class="modal fade" :id="id" tabindex="-1" role="dialog" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4">

          <p class="lead" v-text="introText"></p>
          <p v-text="gettext(explanationText)"></p>
          <p v-text="gettext(splitExplanation)"></p>

          <div class="btn-group mb-4 btn-group-toggle" role="group">
            <button v-text="gettext('Shard Mix')" disabled class="btn btn-outline-secondary"></button>
            <button v-for="option in mixOptions" type="button" @click="setState('mix', option)"
                    :class="['btn btn-outline-primary', mix === option ? 'active': '']"
                    v-text="gettext(option)"></button>
          </div>

          <div class="btn-group mb-4 btn-group-toggle" role="group">
            <button v-text="gettext('Shard Split')" disabled class="btn btn-outline-secondary"></button>
            <button v-for="option in splitOptions" type="button" @click="setState('split', option.value)"
                    :class="['btn btn-outline-primary', split === option.value ? 'active': '']"
                    v-text="gettext('In ' + option.label)"></button>
          </div>

          <div class="btn-group mb-4 btn-group-toggle" role="group">
            <button v-text="gettext('Shard Sort')" disabled class="btn btn-outline-secondary"></button>
            <button v-for="option in sortOptions" type="button" @click="setState('sort', option)"
                    :class="['btn btn-outline-primary', sort === option ? 'active': '']"
                    v-text="gettext('By ' + option)"></button>
          </div>

          <div class="btn-group d-block" role="group">
            <button v-if="!split || !sort || !mix" disabled class="btn btn-secondary disabled"
                    v-text="gettext('Select a count, sort, and mix to open a shard')"></button>
            <button v-else type="button" v-for="(shard, shardIndex) in shardOptions"
                    @click="openShard(shard, shardIndex)"
                    :class="['btn btn-success', index === shardIndex ? 'active': '']"
                    v-text="gettext('Open') + ' ' + gettext(split) + ' ' + shard"></button>
            <button v-if="index !== null" class="btn btn-danger"
                    @click="closeShard()"
                    v-text="gettext('Close Shard')"></button>
          </div>

        </div>
      </div>
    </div>
  </div>

</template>

<script>
import { mapMutations } from 'vuex'
import ModalActionMixin from './ModalActionMixin.vue'

export default {
  mixins: [ModalActionMixin],
  props: { introText: String },
  data: function () {
    // Internal state storing the status of which diversity highlight is being toggled
    return {
      splitOptions: [
        { label: 'Halves', value: 2 },
        { label: 'Thirds', value: 3 },
        { label: 'Quarters', value: 4 },
        { label: 'Fifths', value: 5 },
        { label: 'Sixths', value: 6 },
      ],
      mixOptions: ['Top-to-Bottom', 'Interleaved'],
      sortOptions: ['Bracket', 'Importance'],
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
      if (this.split === 2) {
        return ['A', 'B']
      } else if (this.split === 3) {
        return ['A', 'B', 'C']
      } else if (this.split === 4) {
        return ['A', 'B', 'C', 'D']
      } else if (this.split === 5) {
        return ['A', 'B', 'C', 'D', 'E']
      } else if (this.split === 6) {
        return ['A', 'B', 'C', 'D', 'E', 'F']
      }
      return null
    },
    index () {
      return this.$store.state.sharding.index
    },
    split () {
      return this.$store.state.sharding.split
    },
    mix () {
      return this.$store.state.sharding.mix
    },
    sort () {
      return this.$store.state.sharding.sort
    },
  },
  methods: {
    openShard: function (shardIdentifier, selectedIndex) {
      this.resetModal()
      this.setSharding({ option: 'index', value: selectedIndex })
      $.fn.showAlert('success', `Opened shard ${this.split} ${shardIdentifier}
                                 (sorted by ${this.mix} using ${this.sort})`)
    },
    closeShard: function () {
      this.resetModal()
      this.setState('index', null)
      $.fn.showAlert('success', 'Closed shard')
    },
    setState: function (key, value) {
      this.setSharding({ option: key, value: value })
    },
    ...mapMutations(['setSharding']),
  },
}
</script>
