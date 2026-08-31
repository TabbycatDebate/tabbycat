<script setup>
import { computed } from 'vue'
import { useAjax } from '../composables/useAjax.js'

const props = defineProps({
  cellData: Object,
})

const { ajaxSave } = useAjax()

// Coerce null/undefined (unallocated) to '', matching the plain value=""
// on the Unallocated option.
const displayValue = computed(() => props.cellData.value ?? '')

const sideUpdate = (newValue) => {
  if (props.cellData.noSave) {
    return
  }
  const cd = props.cellData
  const sideValue = newValue === '' ? null : Number(newValue)
  cd.value = sideValue
  cd.sort = sideValue
  const message = `Team ${cd.teamId}'s side for round ${cd.roundId} set to ${sideValue}`
  const payload = { team_id: cd.teamId, round_id: cd.roundId, side: sideValue }
  ajaxSave(cd.saveURL, payload, message, null, null, null)
}
</script>

<template>
  <td :class="cellData.class ? cellData.class : null">
    <span
      v-if="cellData.sort"
      hidden
    >
      {{ cellData.sort }}
    </span>
    <select
      :value="displayValue"
      class="form-control"
      @change="sideUpdate($event.target.value)"
    >
      <option value="">
        {{ cellData.unallocatedLabel }}
      </option>
      <option
        v-for="option in cellData.options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
  </td>
</template>
