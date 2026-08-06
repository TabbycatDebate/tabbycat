<template>

  <td :class="cellData.class ? cellData.class : null" >

    <span v-if="cellData.sort" hidden>
      {{ cellData.sort }}
    </span>
    <select
      :value="displayValue"
      class="form-control"
      @change="sideUpdate($event.target.value)"
    >
      <option value="">{{ cellData.unallocatedLabel }}</option>
      <option v-for="option in cellData.options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>

  </td>

</template>

<script>
import AjaxMixin from '../ajax/AjaxMixin.vue'

export default {
  mixins: [AjaxMixin],
  props: {
    cellData: Object,
  },
  computed: {
    displayValue: function () {
      // Coerce null/undefined (unallocated) to '', matching the plain
      // value="" on the Unallocated <option> (a bound :value="null" would
      // otherwise be stringified to the literal text "null" by the DOM).
      const value = this.cellData.value
      return (value === null || value === undefined) ? '' : value
    },
  },
  methods: {
    sideUpdate: function (newValue) {
      if (this.cellData.noSave) {
        return
      }
      const cd = this.cellData
      const sideValue = newValue === '' ? null : Number(newValue)
      cd.value = sideValue
      cd.sort = sideValue
      const message = `Team ${cd.teamId}'s side for round ${cd.roundId} set to ${sideValue}`
      const payload = { team_id: cd.teamId, round_id: cd.roundId, side: sideValue }
      this.ajaxSave(cd.saveURL, payload, message, null, null, null)
    },
  },
}

</script>
