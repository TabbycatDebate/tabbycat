<template>
  <div class="modal fade" id="confirmAutoImportanceAlert" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p class="lead">assigning will create new importances and remove other ones...</p>

          <p>currently there are X live teams Y dead teams Z safe teams</p>

          <p>this does not account for special break rules and (for BP doesn't account
          for non-general categories. so be sure to check...</p>

          <button type="submit" class="btn btn-block btn-success"
                  @click="createAutoAllocation">
            Assign Automatic Priorities by Bracket
          </button>
          <button type="submit" class="btn btn-block btn-success"
                  @click="createAutoAllocation">
            Assign Automatic Priorities by Liveness
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: { roundInfo: Object, },
  methods: {
    resetAutoAllocationModal: function(button) {
      $('#confirmAutoAllocationAlert').modal('hide')
      $.fn.resetButton(button)
    },
    createAutoAllocation: function(event) {
      var self = this
      $.fn.loadButton(event.target)
      $.post({
        url: this.roundInfo.autoUrl,
        dataType: 'json',
      }).done(function(data, textStatus, jqXHR) {
        // Success handler
        self.$eventHub.$emit('update-allocation', JSON.parse(data.debates))
        self.$eventHub.$emit('update-unallocated', JSON.parse(data.unallocatedAdjudicators))
        self.$eventHub.$emit('update-saved-counter', this.updateLastSaved)
        self.resetAutoAllocationModal(event.target)
        $.fn.showAlert('success', 'Successfully loaded the auto allocation', 10000)
      }).fail(function(response) {
        // Handle Failure
        var info = response.responseJSON.message
        $.fn.showAlert('danger', 'Auto Allocation failed: ' + info, 0)
        self.resetAutoAllocationModal(event.target)
      })
    },
  }
}

</script>
