<template>

  <div :class="['flex-3 flex-truncate d-flex', !confirmed ? 'bg-danger text-white' : '']">
    <div class="align-self-center flex-fill pl-3 ">

      <label class="form-check-label m-0 pl-3 ">
        <input type="checkbox" class="form-check-input" :checked="confirmed" @input="updateStatus">
        <span class="hoverable small"
              v-text="confirmed ? gettext('confirmed') : gettext('unconfirmed')">
        </span>
      </label>

    </div>
  </div>

</template>

<script>
import { mapGetters } from 'vuex'

export default {
  props: {
    debate: Object,
  },
  methods: {
    updateStatus: function (e) {
      const importanceChanges = [{ id: this.debate.id, sides_confirmed: e.target.checked }]
      this.$store.dispatch('updateDebatesOrPanelsAttribute', { sides_confirmed: importanceChanges })
    },
  },
  computed: {
    ...mapGetters(['allDebatesOrPanels']),
    confirmed: function () {
      return this.allDebatesOrPanels[this.debate.id].sides_confirmed
    },
  },
}
</script>
