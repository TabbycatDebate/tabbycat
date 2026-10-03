<script setup>
import { computed, ref } from 'vue'
import FeatherIcon from '../../templates/components/FeatherIcon.vue'
import FormFieldErrors from '../../templates/components/FormFieldErrors.vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { useDraggable } from '../../templates/composables/useDraggable.js'

const props = defineProps({ question: Object, section: Object, editor: Object, canEdit: Boolean })
const { gettext } = useDjangoI18n()
const name = field => props.section.fieldName(props.question.formIndex, field)
const id = field => `id_${name(field)}`
const errors = field => props.question.errors[field] || []
const position = computed(() => props.section.visibleForms.indexOf(props.question))
const update = (field, value) => props.editor.updateQuestion(props.section, props.question.formIndex, field, value)
const visible = field => {
  if (errors(field).length) return true
  if (field === 'choices') return ['ss', 'ms'].includes(props.question.values.answer_type)
  if (['min_value', 'max_value'].includes(field)) return ['i', 'is', 'f'].includes(props.question.values.answer_type)
  return true
}
const width = field => ({ text: 'col-md-8', answer_type: 'col-md-4', min_value: 'col-md-6', max_value: 'col-md-6', help_text: 'col-md-8', name: 'col-md-4' })[field] || 'col-12'
const commonFields = ['text', 'answer_type', 'choices', 'min_value', 'max_value', 'help_text', 'name', 'required']
const fieldOrder = computed(() => [...commonFields, ...Object.keys(props.section.fields).filter(field => !commonFields.includes(field))])
const dropPosition = ref(null)
const { isDragging, dragStart, dragEnd } = useDraggable({
  locked: !props.canEdit,
  get dragPayload () { return { prefix: props.section.prefix, formIndex: props.question.formIndex } },
})
const dragOver = event => {
  if (!props.canEdit || props.question.deleted || !Array.from(event.dataTransfer.types).some(type => ['text', 'text/plain'].includes(type))) return
  event.preventDefault()
  const rect = event.currentTarget.getBoundingClientRect()
  dropPosition.value = event.clientY > rect.top + rect.height / 2 ? 'after' : 'before'
}
const drop = event => {
  event.preventDefault()
  try {
    const payload = JSON.parse(event.dataTransfer.getData('text'))
    if (payload.prefix === props.section.prefix) {
      props.editor.reorder(props.section, payload.formIndex, props.question.formIndex, dropPosition.value === 'after')
    }
  } catch {}
  dropPosition.value = null
}
const move = direction => props.editor.move(props.section, props.question.formIndex, direction)
</script>

<template>
  <div
    class="card mb-3 question-card"
    :class="{ 'question-dragging': isDragging, 'question-drop-before': dropPosition === 'before', 'question-drop-after': dropPosition === 'after' }"
    @dragover="dragOver"
    @dragleave="event => { if (!event.currentTarget.contains(event.relatedTarget)) dropPosition = null }"
    @drop="drop"
  >
    <input
      type="hidden"
      :name="name(section.primaryKey)"
      :value="question.values[section.primaryKey]"
    >
    <input
      type="hidden"
      :name="name('ORDER')"
      :value="position"
    >
    <input
      type="hidden"
      :name="name('DELETE')"
      :value="question.deleted ? 'on' : ''"
    >
    <template v-if="question.deleted">
      <input
        v-for="field in fieldOrder"
        :key="field"
        type="hidden"
        :name="name(field)"
        :value="section.fields[field].kind === 'checkbox' ? (question.values[field] ? 'on' : '') : question.values[field]"
      >
    </template>
    <div class="card-header d-flex align-items-center justify-content-between flex-wrap">
      <div class="d-flex align-items-center">
        <button
          v-if="!question.deleted"
          type="button"
          class="btn btn-sm btn-light mr-2"
          :draggable="canEdit"
          :disabled="!canEdit"
          :aria-label="gettext('Drag to reorder question')"
          @dragstart="dragStart"
          @dragend="dragEnd"
          @keydown.up.prevent="move(-1)"
          @keydown.down.prevent="move(1)"
        >
          <feather-icon name="move" />
        </button>
        <strong>{{ question.values.text || gettext('New question') }}</strong>
      </div>
      <div class="btn-group">
        <template v-if="!question.deleted">
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary"
            :disabled="!canEdit || position === 0"
            :aria-label="gettext('Move question up')"
            @click="move(-1)"
          >
            ↑
          </button>
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary"
            :disabled="!canEdit || position === section.visibleForms.length - 1"
            :aria-label="gettext('Move question down')"
            @click="move(1)"
          >
            ↓
          </button>
          <button
            type="button"
            class="btn btn-sm btn-outline-danger"
            :disabled="!canEdit"
            @click="editor.setDeleted(section, question.formIndex, true)"
          >
            {{ gettext('Remove') }}
          </button>
        </template>
        <button
          v-else
          type="button"
          class="btn btn-sm btn-outline-secondary"
          :disabled="!canEdit"
          @click="editor.setDeleted(section, question.formIndex, false)"
        >
          {{ gettext('Undo removal') }}
        </button>
      </div>
    </div>
    <p
      v-if="question.deleted"
      class="alert alert-warning mb-0"
    >
      {{ gettext('Saving will delete this question and its existing answers.') }}
    </p>
    <div
      v-else
      class="card-body"
    >
      <form-field-errors :errors="question.nonFieldErrors" />
      <form-field-errors :errors="errors(section.primaryKey)" />
      <form-field-errors :errors="errors('ORDER')" />
      <div class="row">
        <template
          v-for="field in fieldOrder"
          :key="field"
        >
          <div
            v-show="visible(field)"
            class="form-group"
            :class="width(field)"
          >
            <label :for="id(field)">
              <input
                v-if="section.fields[field].kind === 'checkbox'"
                :id="id(field)"
                type="checkbox"
                :name="name(field)"
                :checked="question.values[field]"
                :disabled="!canEdit"
                @change="update(field, $event.target.checked)"
              >
              {{ section.fields[field].label }}
            </label>
            <select
              v-if="section.fields[field].kind === 'select'"
              :id="id(field)"
              class="form-control"
              :name="name(field)"
              :value="question.values[field]"
              :disabled="!canEdit"
              @change="update(field, $event.target.value)"
            >
              <option
                v-for="choice in section.fields[field].choices"
                :key="choice[0]"
                :value="choice[0]"
              >
                {{ choice[1] }}
              </option>
            </select>
            <textarea
              v-else-if="section.fields[field].kind === 'textarea'"
              :id="id(field)"
              class="form-control"
              :name="name(field)"
              :rows="field === 'choices' ? 4 : 2"
              :value="question.values[field]"
              :disabled="!canEdit"
              @input="update(field, $event.target.value)"
            />
            <input
              v-else-if="section.fields[field].kind !== 'checkbox'"
              :id="id(field)"
              class="form-control"
              :type="section.fields[field].kind === 'number' && errors(field).length ? 'text' : section.fields[field].kind"
              step="any"
              :name="name(field)"
              :maxlength="section.fields[field].maxLength"
              :value="question.values[field]"
              :disabled="!canEdit"
              @input="update(field, $event.target.value)"
            >
            <small
              v-if="section.fields[field].helpText"
              class="form-text text-muted"
            >{{ section.fields[field].helpText }}</small>
            <form-field-errors :errors="errors(field)" />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.question-dragging { opacity: 0.5; }
.question-drop-before { border-top: 3px solid var(--primary, #6610f2); }
.question-drop-after { border-bottom: 3px solid var(--primary, #6610f2); }
</style>
