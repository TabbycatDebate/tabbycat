<template>
  <div class="modal fade" id="confirmAutoPrioritiseModal"
       tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p class="lead">
            Using auto-prioritise will remove all existing debate priorities and assign new ones.
          </p>
          <p>
            Prioritise <strong>by bracket</strong> will split the draw into quartiles by bracket
            and give higher priorities to higher brackets.
          </p>
          <p>
            Prioritise <strong>by liveness</strong> assign live rooms to be <em>important</em>,
            safe rooms (where all teams are guaranteed to break) to be <em>neutral</em>, and dead
            rooms (where all teams cannot break) to be ¯\_(ツ)_/¯. This is typically only useful in
            the very last preliminary rounds, when many teams are ruled out of the break.
          <p>
            Note that 'liveness' doesn't factor in special break rules other than a strict
            mathematical break. Be sure to double-check the results
          </p>
          <button type="submit" class="btn btn-block btn-success" id="aapb"
                  @click="createAutoPriorities('bracket')">
            Assign Automatic Priorities by Bracket
          </button>
          <button type="submit" class="btn btn-block btn-success mt-4" id="aapl"
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
  props: { roundInfo: Object },
  methods: {
    resetAutoPrioritiesModal: function () {
      $('#confirmAutoPrioritiseModal').modal('hide')
      $.fn.resetButton('#aapb')
      $.fn.resetButton('#aapl')
    },
    createAutoPriorities: function (type) {
      const self = this
      $.fn.loadButton('#aapb')
      $.fn.loadButton('#aapl')
      self.$eventHub.$emit(`assign-importance-by-${type}`)
      $.fn.showAlert('success', `Successfully auto-assigned priorities by ${type}`, 10000)
      self.resetAutoPrioritiesModal()
    },
  },
}

</script>
