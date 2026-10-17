<script setup>
import { computed, ref } from 'vue'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const props = defineProps({
  id: { type: String, required: true },
  label: { type: String, required: true },
  placeholder: String,
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
const { gettext } = useDjangoI18n()
const input = ref(null)
const value = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value),
})

const clear = () => {
  value.value = ''
  input.value.focus()
}
</script>

<template>
  <div
    class="w-100"
    role="search"
  >
    <label
      class="sr-only"
      :for="id"
    >{{ label }}</label>
    <div class="input-group">
      <div
        class="input-group-prepend"
        aria-hidden="true"
      >
        <label
          class="input-group-text justify-content-center search-input-icon"
          :for="id"
        ><i data-feather="search" /></label>
      </div>
      <input
        :id="id"
        ref="input"
        v-model="value"
        class="form-control rounded-right pr-5"
        type="search"
        :placeholder="placeholder"
        autocomplete="off"
      >
      <button
        v-if="modelValue"
        class="btn btn-link text-secondary rounded-right search-input-clear"
        type="button"
        :aria-label="gettext('Clear')"
        @click="clear"
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
input::-webkit-search-cancel-button {
  -webkit-appearance: none;
}

.search-input-clear {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 5;
  width: 2.5rem;
  padding: 0;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  text-decoration: none;
}

.search-input-icon {
  cursor: text;
}

.search-input-icon :deep(.feather) {
  display: block;
  margin: 0;
}
</style>
