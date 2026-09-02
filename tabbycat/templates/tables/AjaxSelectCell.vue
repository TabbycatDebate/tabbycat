<script setup>
import { computed } from 'vue'
import { useAjax } from '../composables/useAjax.js'

const props = defineProps({
  cellData: Object,
})

const emit = defineEmits(['saved'])

const { ajaxSave } = useAjax(time => emit('saved', time))

const displayValue = computed(() => props.cellData.value ?? '')

const selectUpdate = (newValue) => {
  if (props.cellData.noSave) {
    return
  }

  const cd = props.cellData
  const selectedOption = cd.options.find(option => String(option.value) === newValue)
  const selectedValue = newValue === '' ? null : (selectedOption?.value ?? newValue)
  cd.value = selectedValue

  const payload = { ...cd.payload, [cd.payloadKey]: selectedValue }
  ajaxSave(cd.saveURL, payload, cd.saveMessage, null, null, null)
}
</script>

<template>
  <td :class="cellData.class ? cellData.class : null">
    <select
      :value="displayValue"
      class="form-control"
      @change="selectUpdate($event.target.value)"
    >
      <option
        v-if="cellData.blankLabel !== undefined"
        value=""
      >
        {{ cellData.blankLabel }}
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
