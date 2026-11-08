import { computed, reactive, ref } from 'vue'
import { useDjangoFormset } from '../../templates/composables/useDjangoFormset.js'

export function useQuestionEditor (initialData) {
  const dirty = ref(false)
  const normalize = question => ({
    ...question,
    values: { ...question.values },
    errors: { ...question.errors },
    nonFieldErrors: [...question.nonFieldErrors],
  })
  const sections = initialData.sections.map(section => {
    const formset = useDjangoFormset(section.questions, section.management, normalize)
    formset.forms.value.sort((a, b) => {
      const order = question => question.values.ORDER === '' ? Infinity : Number(question.values.ORDER)
      return order(a) - order(b)
    })
    return reactive({
      ...section,
      ...formset,
      systemQuestions: section.systemQuestions.map(question => ({ ...question })),
      // Deleted indices must still be submitted to Django; do not reuse them.
      canAdd: computed(() => initialData.canEdit && formset.nextFormIndex.value < section.management.maxNumForms),
    })
  })
  const mutate = action => {
    if (!initialData.canEdit) return null
    const result = action()
    if (result) dirty.value = true
    return result
  }
  const addQuestion = section => mutate(() => section.canAdd && section.addForm(section.emptyQuestion))
  const updateQuestion = (section, index, name, value) => mutate(() => {
    const question = section.findForm(index)
    if (!question || question.deleted) return null
    question.values[name] = value
    return question
  })
  const setDeleted = (section, index, deleted) => mutate(() => {
    const question = section.findForm(index)
    if (!question) return null
    question.deleted = deleted
    return question
  })
  const reorder = (section, source, target, after = false) => mutate(() => {
    const question = section.findForm(source)
    const destination = section.findForm(target)
    if (!question || !destination || question === destination || question.deleted || destination.deleted) return null
    section.forms.splice(section.forms.indexOf(question), 1)
    section.forms.splice(section.forms.indexOf(destination) + Number(after), 0, question)
    return question
  })
  const move = (section, index, direction) => {
    const position = section.visibleForms.findIndex(question => question.formIndex === index)
    const destination = section.visibleForms[position + direction]
    if (destination) return reorder(section, index, destination.formIndex, direction > 0)
    return null
  }
  const updateSystem = (question, enabled) => mutate(() => {
    if (!initialData.canEditSystem || question.disabled || !question.name) return null
    question.enabled = enabled
    return question
  })
  return { sections, dirty, addQuestion, updateQuestion, setDeleted, reorder, move, updateSystem }
}
