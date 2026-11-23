<script setup>
import { computed, nextTick } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

const props = defineProps({ id: String, options: Array, disabled: Boolean, describedBy: String, invalid: Boolean })
const emit = defineEmits(['update'])
const { gettext, tct } = useDjangoI18n()
const rows = computed(() => props.options.length ? props.options : [null])
const optionId = index => index ? `${props.id}-${index}` : props.id
const focusOption = index => nextTick(() => document.getElementById(optionId(index))?.focus())

const replace = (index, ...replacements) => {
  const options = [...rows.value]
  options.splice(index, 1, ...replacements)
  emit('update', options)
}
const paste = (event, index) => {
  const text = event.clipboardData?.getData('text/plain') || ''
  if (event.target.value || !/[\r\n]/.test(text)) return
  event.preventDefault()
  const options = text.split(/\r\n?|\n/).map(line => line.trim()).filter(Boolean)
  if (options.length) replace(index, ...options)
}
const add = () => {
  const index = rows.value.length
  emit('update', [...rows.value, null])
  focusOption(index)
}
const remove = index => {
  replace(index)
  focusOption(Math.max(index - 1, 0))
}
</script>

<template>
  <div
    v-for="(option, index) in rows"
    :key="index"
    class="input-group mb-2"
  >
    <textarea
      :id="optionId(index)"
      class="form-control"
      :rows="option?.includes('\n') ? 2 : 1"
      :aria-label="tct('Option %s', [index + 1])"
      :aria-describedby="describedBy"
      :aria-invalid="invalid || undefined"
      :value="option"
      :disabled="disabled"
      @input="replace(index, $event.target.value || null)"
      @paste="paste($event, index)"
    />
    <div
      v-if="rows.length > 1 || option !== null"
      class="input-group-append"
    >
      <button
        type="button"
        class="btn btn-outline-secondary"
        :aria-label="tct('Remove option %s', [index + 1])"
        :disabled="disabled"
        @click="remove(index)"
      >
        ×
      </button>
    </div>
  </div>
  <button
    type="button"
    class="btn btn-sm btn-outline-secondary"
    :disabled="disabled"
    @click="add"
  >
    {{ gettext('Add option') }}
  </button>
</template>
