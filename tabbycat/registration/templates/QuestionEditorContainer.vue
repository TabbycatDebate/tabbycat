<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import DjangoFormsetManagement from '../../templates/components/DjangoFormsetManagement.vue'
import FormFieldErrors from '../../templates/components/FormFieldErrors.vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import QuestionEditorCard from './QuestionEditorCard.vue'
import { useQuestionEditor } from './useQuestionEditor.js'

const { initialData } = defineProps({ initialData: Object })
const { gettext } = useDjangoI18n()
const editor = useQuestionEditor(initialData)
const { sections, dirty } = editor
const submitting = ref(false)
let form = null
const add = section => {
  const question = editor.addQuestion(section)
  if (question) nextTick(() => document.getElementById(`id_${section.fieldName(question.formIndex, 'text')}`)?.focus())
}
const beforeUnload = event => {
  if (!dirty.value || submitting.value) return
  event.preventDefault()
  event.returnValue = ''
}
const submit = () => { submitting.value = true }
onMounted(() => {
  form = document.getElementById('question-editor')
  form?.addEventListener('submit', submit)
  window.addEventListener('beforeunload', beforeUnload)
})
onBeforeUnmount(() => {
  form?.removeEventListener('submit', submit)
  window.removeEventListener('beforeunload', beforeUnload)
})
</script>

<template>
  <fieldset :disabled="!initialData.canEdit">
    <section
      v-for="(section, index) in sections"
      :key="section.prefix"
      class="mb-4 question-section"
      :aria-labelledby="`heading-${section.prefix}`"
    >
      <h3 :id="`heading-${section.prefix}`">
        {{ index + 1 }}. {{ section.title }}
      </h3>
      <div class="card mb-3">
        <div class="card-header">
          {{ gettext('Built-in questions') }}
        </div>
        <div class="list-group list-group-flush">
          <div
            v-for="(question, systemIndex) in section.systemQuestions"
            :key="systemIndex"
            class="list-group-item"
          >
            <div class="d-flex justify-content-between align-items-center">
              <label
                v-if="question.name"
                class="mb-0"
                :for="`id_${question.name}`"
              >
                <input
                  :id="`id_${question.name}`"
                  type="checkbox"
                  :name="question.name"
                  :checked="question.enabled"
                  :disabled="!initialData.canEditSystem || question.disabled"
                  @change="editor.updateSystem(question, $event.target.checked)"
                >
                {{ question.label }}
              </label>
              <strong v-else>{{ question.label }}</strong>
              <span class="badge badge-light">{{ question.type }}</span>
            </div>
            <small
              v-if="question.help_text"
              class="text-muted d-block"
            >{{ question.help_text }}</small>
            <small
              v-if="question.condition"
              class="text-muted d-block"
            >{{ question.condition }}</small>
            <small
              v-if="!question.name"
              class="text-muted"
            >
              {{ gettext('Included by tournament settings') }}<template v-if="question.required"> · {{ gettext('Required') }}</template>
            </small>
          </div>
        </div>
      </div>
      <p
        v-if="!initialData.canEditSystem && section.systemQuestions.some(question => question.name)"
        class="text-muted"
      >
        {{ gettext('Editing built-in questions requires permission to edit tournament settings.') }}
      </p>
      <django-formset-management
        :management="section.management"
        :total-forms="section.nextFormIndex"
      />
      <form-field-errors :errors="section.nonFormErrors" />
      <question-editor-card
        v-for="question in section.forms"
        :key="question.formIndex"
        :question="question"
        :section="section"
        :editor="editor"
        :can-edit="initialData.canEdit"
      />
      <button
        type="button"
        class="btn btn-outline-primary"
        :disabled="!section.canAdd"
        @click="add(section)"
      >
        + {{ gettext('Add question') }}
      </button>
    </section>
    <button
      type="submit"
      class="btn btn-success btn-block"
    >
      {{ gettext('Save Questions') }}
    </button>
  </fieldset>
</template>
