<template>

    <nav class="navbar navbar-default navbar-light fixed-top">

      <div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups">
        <div class="btn-group btn-group-sm">
          <a :href="$store.state.roundInfo.backUrl" class="btn btn-outline-primary"
             data-toggle="tooltip" data-placement="bottom" :title="gettext('Return to Draw')">
            <i data-feather="chevron-left"></i>
          </a>
          <auto-save-counter></auto-save-counter>
        </div>
        <div class="btn-group btn-group-sm ml-2">
          <slot name="actions"></slot>
        </div>
      </div>

    </nav>

</template>

<script>
import AutoSaveCounter from './AutoSaveCounter.vue'

export default {
  components: { AutoSaveCounter },
  methods: {
    showModal: function (modalName) {
      $(modalName).modal('show')
    },
    titleCase: function (title) {
      return title.charAt(0).toUpperCase() + title.substr(1)
    },
    toggleHighlight: function (highlight, oldState) {
      this.highlights.forEach((value) => {
        value.state = false
      })
      highlight.state = !oldState
      // Turn off all highlights; toggle the one just clicked
      // TODO: highlight action
    },
  },
}

</script>
