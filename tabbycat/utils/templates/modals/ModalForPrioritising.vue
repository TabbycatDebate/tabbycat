<template>

  <div class="modal fade" :id="id" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4">

          <p class="lead" v-text="introText"></p>
          <p v-text="gettext(`Prioritise by bracket will split the draw into quartiles by bracket
                              and give higher priorities to higher brackets.`)"></p>
          <p v-text="gettext(`Prioritise by liveness assign live rooms to be important,
                              safe rooms (where all teams are guaranteed to break) to be neutral>,
                              and dead rooms (where all teams cannot break) to be meh. This is
                              typically only useful in the very last preliminary rounds, when many
                              teams are ruled out of the break.`)"></p>
          <p v-text="gettext(`Note that 'liveness' doesn't factor in special rules other than a
                              strict mathematical break. Be sure to double-check the results`)"></p>

          <button type="submit" class="btn btn-block btn-success"
                  @click="createAutoPrioritisation('bracket')"
                  v-text="gettext('Assign Automatic Priorities by Bracket')"></button>
          <button type="submit" class="btn btn-block btn-success mt-4"
                  @click="createAutoPrioritisation('liveness')"
                  v-text="gettext('Assign Automatic Priorities by Liveness')"></button>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
export default {
  props: { introText: String },
  data: function () {
    // Internal state storing the status of which diversity highlight is being toggled
    return {
      id: 'confirmPrioritiseModal',
    }
  },
  computed: {

  },
  methods: {
    resetModal: function () {
      $(this.id).modal('hide')
    },
    createAutoPrioritisation: function (type) {
      this.resetModal()
    },
  },
}
</script>
