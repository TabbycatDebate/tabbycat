<script setup>
import _ from 'lodash'
import { useAjax } from '../composables/useAjax.js'

const props = defineProps({
  cellData: Object,
})

const emit = defineEmits(['toggle-checked', 'update-sort'])

const { ajaxSave } = useAjax()

const checkUpdate = (newChecked) => {
  if (props.cellData.noSave) {
    return
  }
  const cd = props.cellData
  cd.checked = newChecked
  cd.sort = newChecked
  if (_.isUndefined(props.cellData.saveURL)) {
    emit('toggle-checked', cd)
  } else {
    const message = `${cd.id}'s ${cd.type} status as ${newChecked}`
    const payload = { id: cd.id }
    payload[cd.type] = newChecked
    ajaxSave(cd.saveURL, payload, message, null, null, null)
  }
  emit('update-sort', { id: cd.id, sort: newChecked })
}
</script>

<template>
  <td :class="cellData.class ? cellData.class : null">
    <span
      v-if="cellData.sort"
      hidden
    >
      {{ cellData.checked }}
    </span>
    <div class="table-check">
      <input
        :checked="cellData.checked"
        type="checkbox"
        class="form-check-input position-static"
        :name="cellData.name"
        :value="cellData.value"
        @change="checkUpdate($event.target.checked)"
      >
    </div>
  </td>
</template>
