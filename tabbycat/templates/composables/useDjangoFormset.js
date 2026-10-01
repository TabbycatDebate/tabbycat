import { computed, ref } from 'vue'

export function useDjangoFormset (initialForms, management, normalizeForm = form => ({ ...form })) {
  const forms = ref(initialForms.map(form => normalizeForm(form)))
  const nextFormIndex = ref(Number(management.totalForms))
  const maximumForms = management.maxNumForms === '' || management.maxNumForms == null
    ? Infinity
    : Number(management.maxNumForms)

  const visibleForms = computed(() => forms.value.filter(form => !form.deleted))
  const deletedForms = computed(() => forms.value.filter(form => form.deleted))
  const canAdd = computed(() => !Number.isFinite(maximumForms) || visibleForms.value.length < maximumForms)

  const findForm = formIndex => forms.value.find(form => form.formIndex === formIndex)
  const fieldName = (formIndex, field) => `${management.prefix}-${formIndex}-${field}`

  const addForm = values => {
    if (!canAdd.value) return null
    const form = normalizeForm({
      ...values,
      formIndex: nextFormIndex.value++,
      deleted: false,
    })
    forms.value.push(form)
    return form
  }

  const deleteForm = formIndex => {
    const form = findForm(formIndex)
    if (!form) return null
    form.deleted = true
    return form
  }

  return {
    canAdd,
    deletedForms,
    forms,
    visibleForms,
    nextFormIndex,
    addForm,
    deleteForm,
    fieldName,
    findForm,
  }
}
