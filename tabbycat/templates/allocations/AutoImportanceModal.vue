<template>
  <div class="modal fade" id="confirmAutoPrioritiseModal" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p class="lead">Using auto-prioritise will remove all existing debate priorities and assign new ones.</p>
          <p>Prioritise <strong>by bracket</strong> will split the draw into quartiles by bracket and give higher priorities to higher brackets. Teams on fewer points will receive lower priorities and vice versa.</p>
          <p>Prioritise <strong>by liveness</strong> will split the draw into quartiles by the number of 'live' teams within each room and give lower priorities to rooms that cannot break. This is only useful in the final couple of rounds before a break round (currently there are only X safe teams and Y dead teams).
          <p>Note that 'liveness' doesn't factor in special break rules other than a strict mathematical break. IF BP: doesn't support secondary break categories (e.g. Novice, ESL). Be sure to review the results.</p>
          <p>With either option the highest priority setting is not specified so that it can be used as an easy override</p>

          <button type="submit" class="btn btn-block btn-success"
                  @click="createAutoPriorities('bracket')">
            Assign Automatic Priorities by Bracket
          </button>
          <button type="submit" class="btn btn-block btn-success"
                  @click="createAutoPriorities('liveness')">
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
    resetAutoPrioritiesModal: function(button) {
      $('#confirmAutoPrioritiseModal').modal('hide')
      $.fn.resetButton(button)
    },
    createAutoPriorities: function(event) {
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
