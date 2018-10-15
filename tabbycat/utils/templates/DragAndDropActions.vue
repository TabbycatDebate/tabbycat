<template>

    <nav class="navbar navbar-default navbar-light fixed-top px-2">

      <div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups">
        <div class="btn-group btn-group-sm">
          <a :href="extra.backUrl" class="btn btn-outline-primary"
             data-toggle="tooltip" data-placement="bottom" :title="gettext('Return to Draw')">
            <i data-feather="chevron-left"></i>
          </a>
          <auto-save-counter></auto-save-counter>
        </div>
        <div class="btn-group btn-group-sm ml-2">
          <a v-if="prioritise" class="btn text-white btn-success" @click="$emit('prioritise')"
             v-text="gettext('Auto-Prioritise')"></a>
          <a v-if="allocate" class="btn text-white btn-success" @click="$emit('allocate')"
             v-text="gettext('Auto-Allocate')"></a>
          <a v-if="shard" class="btn text-white btn-success" @click="$emit('shard')">
            <i data-feather="server"></i>
          </a>
        </div>
      </div>

      <div class="btn-group btn-group-sm">
        <template v-if="!currentHighlightKey">
          <slot name="default-highlights"></slot>
        </template>
        <template v-else>
          <button class="btn btn-outline-secondary disabled" v-text="gettext('Key')"></button>
          <button v-for="option in highlights[currentHighlightKey].options"
                  :class="['btn btn-primary', option.css]">
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
  props: ['prioritise', 'allocate', 'shard'],
  methods: {
    titleCase: function (title) {
      return title.charAt(0).toUpperCase() + title.substr(1)
    },
    ...mapMutations(['toggleHighlight']),
    startShard: function (event) {
      window.alert('sharding')
    },
  },
  computed: {
    currentHighlightKey: function () {
      let currentKey = Object.keys(this.highlights).filter(key => this.highlights[key].active)
      if (currentKey.length > 0) {
        return currentKey[0]
      }
      return false
    },
    ...mapState(['highlights', 'extra']),
  },
}
</script>
