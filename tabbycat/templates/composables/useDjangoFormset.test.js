import assert from 'node:assert/strict'
import test from 'node:test'
import { useDjangoFormset } from './useDjangoFormset.js'

test('keeps stable form indices and deleted forms when adding replacements', () => {
  const formset = useDjangoFormset([
    { formIndex: 0, title: 'First', deleted: false },
    { formIndex: 1, title: 'Second', deleted: false },
  ], {
    prefix: 'form',
    totalForms: 2,
    maxNumForms: 2,
  })

  assert.equal(formset.canAdd.value, false)
  formset.deleteForm(0)
  assert.equal(formset.canAdd.value, true)

  const replacement = formset.addForm({ title: 'Replacement' })

  assert.equal(replacement.formIndex, 2)
  assert.equal(formset.fieldName(replacement.formIndex, 'title'), 'form-2-title')
  assert.equal(formset.nextFormIndex.value, 3)
  assert.deepEqual(formset.visibleForms.value.map(form => form.formIndex), [1, 2])
  assert.deepEqual(formset.deletedForms.value.map(form => form.formIndex), [0])
})

test('normalizes initial and newly added forms', () => {
  const normalize = form => ({ ...form, errors: { ...(form.errors || {}) } })
  const formset = useDjangoFormset([
    { formIndex: 0, errors: { title: ['Required'] } },
  ], {
    totalForms: 1,
    maxNumForms: 10,
  }, normalize)

  const added = formset.addForm({})

  assert.deepEqual(formset.forms.value[0].errors, { title: ['Required'] })
  assert.deepEqual(added.errors, {})
})
