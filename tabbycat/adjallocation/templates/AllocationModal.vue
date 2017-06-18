<template>
  <div class="modal fade" id="confirmAutoAlert" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p class="lead">Using auto-allocate will <strong>remove all existing adjudicator
          allocations</strong> and create new panels for all debates.</p>
          <p>The allocator forms stronger panels for debates that have been assigned higher
          importances. If importances have not been set, or are equivalent, it will give
          stronger panels to debates in a higher bracket.</p>
          <p>Adjudicators must have a feedback score over <strong>{{ roundInfo.scoreForVote }}</strong>
          to panel. You can change this in the <em>Draw Rules</em> section of Configuration if needed.
          Try modifying this value if you are seeing too few or too many panellists being allocated.</p>
          <div v-if="roundInfo.scoreForVote > roundInfo.scoreMax" class="alert alert-warning">
            The score required to panel ({{ roundInfo.scoreForVote }}) is higher than the maximum
            adjudicator score ({{ roundInfo.scoreMax }}). You should probably lower the score required
            to panel in settings.
          </div>
          <div v-if="roundInfo.scoreForVote < roundInfo.scoreMin" class="alert alert-warning">
            The score required to panel ({{ roundInfo.scoreForVote }}) is lower than the minimum
            adjudicator score ({{ roundInfo.scoreMin }}). You should probably raise the score
            required to panel in settings.
          </div>
          <button type="submit" class="btn btn-block btn-success"
                  @click="createAutoAllocation"
                  data-loading-text="Loading Auto Allocation...">
            Create Automatic Allocation
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
      $(button).button('reset');
      $('#confirmAutoAlert').modal('hide');
    },
    createAutoAllocation: function(event) {
      var self = this
      $(event.target).button('loading')
      $.post({
        url: this.roundInfo.autoUrl,
        success: function(data, textStatus, jqXHR) {
          self.resetAutoAllocationModal(event.target)
          $.fn.showAlert('success', '<strong>Success:</strong> loaded the auto allocation', 10000)
          self.$eventHub.$emit('update-allocation', JSON.parse(data.debates))
          self.$eventHub.$emit('update-unallocated', JSON.parse(data.unallocatedAdjudicators))
          self.$eventHub.$emit('update-saved-counter', this.updateLastSaved)
        },
        error: function(data, textStatus, jqXHR) {
          self.resetAutoAllocationModal(event.target)
          $.fn.showAlert('danger', '<strong>Auto Allocation failed:</strong> ' + data.responseText, 0)
        },
        dataType: "json"
      });
    },
  }
}

</script>
