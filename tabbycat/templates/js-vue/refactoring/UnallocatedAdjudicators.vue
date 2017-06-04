<template>

  <nav
    v-on:dragover.prevent
    v-on:dragenter="dragEnter"
    v-on:dragleave="dragLeave"
    v-on:drop="drop"
    v-bind:class="{ 'vue-is-drag-enter': isDroppable }"
    class="navbar navbar-default navbar-fixed-bottom vue-droppable unallocated-adjs">

    <debate-adjudicator v-if="roundInfo.roundIsPrelim"
      v-for="adj in adjudicatorsOrderedByScore" :adjorteam="adj">
    </debate-adjudicator>
    <debate-adjudicator v-if="!roundInfo.roundIsPrelim"
      v-for="adj in adjudicatorsOrderedByName" :adjorteam="adj">
    </debate-adjudicator>

  </nav>

</template>

<script>
import DebateAdjudicator from './DebateAdjudicator.vue'
import DroppableMixin from '../draganddrops/DroppableMixin.vue'
import _ from 'lodash'

export default {
  mixins: [DroppableMixin],
  props: {
    adjudicators: Array,
    roundInfo: Object
  },
  computed: {
    adjudicatorsOrderedByName: function() {
      return _.orderBy(this.adjudicators, 'name', ['asc'])
    },
    adjudicatorsOrderedByScore: function() {
      return _.orderBy(this.adjudicators, 'score', ['desc'])
    }
  },
  components: {
    'DebateAdjudicator': DebateAdjudicator
  },
  methods: {
    handleDrop: function(ev) {
      this.$dispatch('set-adj-unused');
    }
  }
}
</script>