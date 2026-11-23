<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
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
const errorSummary = ref(null)
const conflictSections = initialData.conflictSections
const errorLinks = computed(() => {
  const links = []
  for (const section of sections) {
    if (section.nonFormErrors.length) {
      links.push({ target: `heading-${section.prefix}`, label: section.title, messages: section.nonFormErrors })
    }
    for (const question of section.visibleForms) {
      const label = question.values.text || gettext('New question')
      const heading = `id_${section.fieldName(question.formIndex, 'heading')}`
      const questionLabel = `${section.title} · ${label}`
      const generalErrors = [...question.nonFieldErrors]
      for (const [field, messages] of Object.entries(question.errors)) {
        if (section.fields[field]) {
          links.push({
            target: `id_${section.fieldName(question.formIndex, field)}`,
            label: `${questionLabel} · ${section.fields[field].label}`,
            messages,
          })
        } else {
          generalErrors.push(...messages)
        }
      }
      if (generalErrors.length) links.push({ target: heading, label: questionLabel, messages: generalErrors })
    }
  }
  return links
})

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
const submit = event => {
  if (conflictSections.length) {
    event.preventDefault()
    errorSummary.value?.focus()
    return
  }
  submitting.value = true
}
const goToError = target => {
  const field = document.getElementById(target)
  field?.scrollIntoView({ block: 'center' })
  field?.focus({ preventScroll: true })
}
onMounted(() => {
  form = document.getElementById('question-editor')
  form?.addEventListener('submit', submit)
  window.addEventListener('beforeunload', beforeUnload)
  errorSummary.value?.focus()
})
onBeforeUnmount(() => {
  form?.removeEventListener('submit', submit)
  window.removeEventListener('beforeunload', beforeUnload)
})
</script>

<template>
  <fieldset :disabled="!initialData.canEdit">
    <div
      v-if="initialData.saveFailed"
      ref="errorSummary"
      class="alert alert-danger"
      role="region"
      aria-labelledby="question-editor-error-title"
      tabindex="-1"
    >
      <h2
        id="question-editor-error-title"
        class="h5"
      >
        {{ gettext('Changes were not saved') }}
      </h2>
      <template v-if="conflictSections.length">
        <p>{{ gettext('These sections changed while you were editing. Your draft is still on this page.') }}</p>
        <ul>
          <li
            v-for="title in conflictSections"
            :key="title"
          >
            {{ title }}
          </li>
        </ul>
        <a
          class="alert-link"
          :href="initialData.latestUrl"
          target="_blank"
          rel="noopener"
        >{{ gettext('Open the latest version in a new tab to compare changes') }}</a>
      </template>
      <ul
        v-else
        class="mb-0"
      >
        <li
          v-for="error in errorLinks"
          :key="error.target"
          class="mb-1"
        >
          <a
            class="alert-link"
            :href="`#${error.target}`"
            @click.prevent="goToError(error.target)"
          >{{ error.label }}</a>
          <span> · {{ error.messages.join(' ') }}</span>
        </li>
      </ul>
    </div>
    <section
      v-for="section in sections"
      :key="section.prefix"
      class="mb-4 question-section"
      :aria-labelledby="`heading-${section.prefix}`"
    >
      <div class="d-flex flex-wrap align-items-center justify-content-between mb-2">
        <h3
          :id="`heading-${section.prefix}`"
          class="mb-1 mr-2"
          tabindex="-1"
        >
          {{ section.title }}
        </h3>
        <button
          type="button"
          class="btn btn-outline-primary mb-1"
          :disabled="!section.canAdd"
          @click="add(section)"
        >
          + {{ gettext('Add question') }}
        </button>
      </div>
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
      <input
        type="hidden"
        :name="`${section.prefix}-revision`"
        :value="section.revision"
      >
      <form-field-errors :errors="section.nonFormErrors" />
      <question-editor-card
        v-for="question in section.forms"
        :key="question.formIndex"
        :question="question"
        :section="section"
        :editor="editor"
        :can-edit="initialData.canEdit"
      />
    </section>
    <div
      v-if="initialData.canEdit"
      class="question-editor-actions d-flex justify-content-end bg-white border-top p-2"
    >
      <button
        type="submit"
        class="btn btn-success"
        :disabled="!!conflictSections.length"
      >
        {{ gettext('Save Questions') }}
      </button>
    </div>
  </fieldset>
</template>

<style scoped>
.question-editor-actions {
  position: sticky;
  bottom: 0;
  z-index: 10;
}
</style>
