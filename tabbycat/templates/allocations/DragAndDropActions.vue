<template>

    <nav class="navbar navbar-default navbar-light fixed-top px-2">

      <div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups">
        <div class="btn-group btn-group-sm">
          <a :href="extra.backUrl" class="btn btn-outline-primary"
             data-toggle="tooltip" data-placement="bottom" :title="extra.backLabel">
            <i data-feather="chevron-left"></i>
          </a>
          <auto-save-counter></auto-save-counter>
          <slot name="extra-actions"></slot>
          <button v-if="prioritise" @click="$emit('show-prioritise')"
                  :class="['btn btn-outline-primary', count > 0 ? '' : 'disabled btn-no-hover']"
                  v-text="gettext('Prioritise')"></button>
          <button v-if="allocate" @click="$emit('show-allocate')"
                  :class="['btn btn-outline-primary', count > 0 ? '' : 'disabled btn-no-hover']"
                  v-text="gettext('Allocate')"></button>
          <button v-if="shard" @click="$emit('show-shard')"
                  :class="['btn ', count > 0 ? '' : 'disabled btn-no-hover',
                                   shardingEnabled ? 'btn-primary' : 'btn-outline-primary']" >
            <i data-feather="server"></i>
          </button>
        </div>
        <div class="dropdown">
          <button class="btn btn-sm ml-2 btn-outline-primary dropdown-toggle"
                  data-toggle="dropdown" id="dropdownMenuOffset" title="Sort the draw">
            <i data-feather="list"></i>
          </button>
          <div class="dropdown-menu" aria-labelledby="dropdownMenuOffset">
            <a class="dropdown-item" href="#" @click="setSorting('room_rank')">
              <span v-if="isElimination" >Sort by Break Rank</span>
              <span v-if="!isElimination" >Sort by Room Rank</span>
            </a>
            <a v-if="!isElimination" class="dropdown-item" href="#" @click="setSorting('bracket')">
              Sort by Bracket
            </a>
            <a class="dropdown-item" href="#" @click="setSorting('importance')">
              Sort by Importance
            </a>
            <a v-if="!isElimination" class="dropdown-item" href="#" @click="setSorting('liveness')">
              Sort by Liveness
            </a>
          </div>
        </div>
      </div>

      <div class="btn-group btn-group-sm">
        <button class="btn btn-outline-secondary disabled d-xl-inline d-none"
                data-toggle="tooltip" :title="('Key for the color highlights.')">
          <i data-feather="help-circle"></i>
        </button>
        <template v-if="!currentHighlightKey">
          <slot name="default-highlights"></slot>
          <button class="btn btn-dark" v-text="gettext('Unavailable')" data-toggle="tooltip"
                :title="('Has not been marked as available for this round or has been allocated twice.')"></button>
        </template>
        <template v-else>
          <button v-for="option in highlights[currentHighlightKey].options"
                  :class="['btn btn-primary border-0', currentHighlightKey + '-display', option.css]">
            {{ option.fields.name }}
          </button>
        </template>
      </div>

      <div class="btn-group btn-group-sm">
        <button v-for="(highlight, highlightKey) in highlights"
                @click="toggleHighlight(highlightKey)"
                :class="['btn btn-outline-primary', highlight.active ? 'btn-primary active' : '']">
          <span :class="highlight.active ? 'd-none' : ''"><i data-feather="eye"></i></span>
          <span :class="highlight.active ? '' : 'd-none'"><i data-feather="eye-off"></i></span>
          <span class="pl-1" v-text="gettext(titleCase(highlightKey))"></span>
        </button>
      </div>

    </nav>

</template>

<script>
import { mapMutations, mapState } from 'vuex'

import AutoSaveCounter from './AutoSaveCounter.vue'

export default {
  components: { AutoSaveCounter },
  props: ['prioritise', 'allocate', 'shard', 'count'],
  methods: {
    titleCase: function (title) {
      return title.charAt(0).toUpperCase() + title.substr(1)
    },
    ...mapMutations(['toggleHighlight', 'setSorting']),
  },
  computed: {
    isElimination: function () {
      return this.$store.state.round.stage === 'E'
    },
    currentHighlightKey: function () {
      const currentKey = Object.keys(this.highlights).filter(key => this.highlights[key].active)
      if (currentKey.length > 0) {
        return currentKey[0]
      }
      return false
    },
    shardingEnabled: function () {
      return this.$store.state.sharding.index !== null
    },
    ...mapState(['highlights', 'extra']),
  },
}
</script>
