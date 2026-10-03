import assert from 'node:assert/strict'
import test from 'node:test'
import { useQuestionEditor } from './useQuestionEditor.js'

const question = (formIndex, order = formIndex, deleted = false) => ({
  formIndex, deleted,
  values: { id: formIndex + 1, ORDER: order, text: `Question ${formIndex}`, answer_type: 't', choices: '', required: true },
  errors: {}, nonFieldErrors: [],
})
const initialData = (canEdit = true) => ({
  canEdit, canEditSystem: canEdit,
  sections: ['team', 'speaker'].map(prefix => ({
    prefix, management: { prefix, totalForms: 2, initialForms: 2, maxNumForms: 5 },
    questions: [question(0, 1), question(1, 0)],
    emptyQuestion: question(null),
    systemQuestions: [{ name: `${prefix}-system-email`, enabled: false, disabled: false }],
  })),
})

test('restores submitted ordering without changing Django form indices', () => {
  const editor = useQuestionEditor(initialData())
  const [team, speaker] = editor.sections
  assert.deepEqual(team.forms.map(q => q.formIndex), [1, 0])
  editor.move(team, 0, -1)
  assert.deepEqual(team.visibleForms.map(q => q.formIndex), [0, 1])
  assert.deepEqual(speaker.visibleForms.map(q => q.formIndex), [1, 0])
  assert.equal(team.fieldName(0, 'text'), 'team-0-text')
  assert.equal(editor.dirty.value, true)
})

test('add, remove and undo preserve values and monotonically increasing indices', () => {
  const editor = useQuestionEditor(initialData())
  const team = editor.sections[0]
  const added = editor.addQuestion(team)
  assert.equal(added.formIndex, 2)
  editor.updateQuestion(team, 2, 'choices', 'Vegan\nVegetarian, with dairy')
  editor.setDeleted(team, 2, true)
  assert.equal(team.visibleForms.length, 2)
  const next = editor.addQuestion(team)
  assert.equal(next.formIndex, 3)
  editor.setDeleted(team, 2, false)
  assert.equal(team.findForm(2).values.choices, 'Vegan\nVegetarian, with dairy')
  assert.equal(team.nextFormIndex, 4)
  assert.notEqual(team.findForm(2).values, team.findForm(3).values)
})

test('reordering ignores deleted, missing and same-row targets', () => {
  const editor = useQuestionEditor(initialData())
  const team = editor.sections[0]
  editor.setDeleted(team, 0, true)
  const order = team.forms.map(q => q.formIndex)
  editor.reorder(team, 1, 0)
  editor.reorder(team, 1, 99)
  editor.reorder(team, 1, 1)
  assert.deepEqual(team.forms.map(q => q.formIndex), order)
})

test('read-only state rejects question and system field mutations', () => {
  const editor = useQuestionEditor(initialData(false))
  const team = editor.sections[0]
  assert.equal(editor.addQuestion(team), null)
  editor.updateQuestion(team, 0, 'text', 'Changed')
  editor.setDeleted(team, 0, true)
  editor.move(team, 0, -1)
  editor.updateSystem(team.systemQuestions[0], true)
  assert.equal(team.findForm(0).values.text, 'Question 0')
  assert.equal(team.findForm(0).deleted, false)
  assert.equal(team.systemQuestions[0].enabled, false)
  assert.equal(editor.dirty.value, false)
})

test('question editing does not grant permission to change system fields', () => {
  const data = initialData()
  data.canEditSystem = false
  const editor = useQuestionEditor(data)
  editor.updateSystem(editor.sections[0].systemQuestions[0], true)
  assert.equal(editor.sections[0].systemQuestions[0].enabled, false)
})

test('caps total forms including removed forms to preserve Django management limits', () => {
  const editor = useQuestionEditor(initialData())
  const team = editor.sections[0]
  for (let i = 0; i < 3; i++) editor.addQuestion(team)
  editor.setDeleted(team, 2, true)
  assert.equal(team.canAdd, false)
  assert.equal(editor.addQuestion(team), false)
  assert.equal(team.nextFormIndex, 5)
})
