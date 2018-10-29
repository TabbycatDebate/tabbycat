<template>

  <div class="modal fade" :id="id" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4">

          <p class="lead" v-text="introText"></p>
          <button type="submit" @click="createPreformedPanels"
                  :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                  v-text="gettext('Create Preformed Panels')"></button>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
export default {
  props: { introText: String, contextOfAction: String },
  data: function () {
    // Internal state storing the status of which diversity highlight is being toggled
    return {
      id: 'confirmCreatePreformedPanelsModal',
      loading: false,
    }
  },
  methods: {
    resetModal: function () {
      $(this.id).modal('hide')
    },
    createPreformedPanels: function (shardIdentifier, index) {
      this.$store.state.wsBridge.send({
        'action': this.contextOfAction,
      })
    },
  },
}
</script>
