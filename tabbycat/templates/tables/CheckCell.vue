<script setup>
import _ from 'lodash'
import { inject } from 'vue'
import { useAjax } from '../composables/useAjax.js'

const props = defineProps({
  cellData: Object,
})

const emit = defineEmits(['toggle-checked', 'update-sort'])

const { ajaxSave } = useAjax()
const drag = inject('checkboxDrag', null)

const checkUpdate = (newChecked) => {
  if (props.cellData.noSave || props.cellData.disabled) {
    return
  }
  if (props.cellData.dragSelect && props.cellData.checked === newChecked) return
  const cd = props.cellData
  cd.checked = newChecked
  cd.sort = newChecked

  if (props.cellData.noSave) {
    return
  }

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

const startDrag = (event) => {
  if (!props.cellData.dragSelect || !drag || props.cellData.disabled || event.button !== 0) return
  event.preventDefault()
  drag.checked = !props.cellData.checked
  checkUpdate(drag.checked)
}

const continueDrag = (event) => {
  if (!props.cellData.dragSelect || !drag || drag.checked === null) return
  if (event.buttons !== 1) {
    drag.checked = null
    return
  }
  checkUpdate(drag.checked)
}
</script>

<template>
  <td
    :class="cellData.class ? cellData.class : null"
    @mousedown="startDrag"
    @mouseenter="continueDrag"
  >
    <span
      v-if="cellData.sort"
      hidden
    >
      {{ cellData.checked }}
    </span>
    <div class="table-check">
      <input
        :checked="cellData.checked"
        :disabled="cellData.disabled"
        :title="cellData.disabled ? cellData.disabledTooltip : null"
        type="checkbox"
        class="form-check-input position-static"
        :name="cellData.name"
        :value="cellData.value"
        :aria-label="cellData.label"
        @click="cellData.dragSelect && $event.detail > 0 && $event.preventDefault()"
        @change="checkUpdate($event.target.checked)"
      >
    </div>
  </td>
</template>
