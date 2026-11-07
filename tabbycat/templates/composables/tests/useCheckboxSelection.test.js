import assert from 'node:assert/strict'
import { test } from 'node:test'
import { useCheckboxSelection } from '../useCheckboxSelection.js'

const checkbox = (extra = {}) => ({ component: 'check-cell', checked: false, ...extra })

test('selects a rectangle in either direction, skipping disabled and ordinary cells', () => {
  const rows = [
    [checkbox(), { text: 'A' }, checkbox()],
    [checkbox({ disabled: true }), { text: 'B' }, checkbox({ noSave: true })],
    [checkbox(), { text: 'C' }, checkbox()],
  ]
  const state = useCheckboxSelection()
  for (const [start, end] of [[[0, 0], [2, 2]], [[2, 2], [0, 0]]]) {
    state.start(rows, ...start)
    state.extend(...end)
    assert.deepEqual([...state.selected.value], [rows[0][0], rows[0][2], rows[1][2], rows[2][0], rows[2][2]])
    assert.equal(rows[0][0].checked, false, 'selection does not change checkbox values')
    state.stop()
  }
})

test('uses the visible row order and shrinks the selection when dragging back', () => {
  const hidden = [checkbox()]
  const a = [checkbox()]
  const b = [checkbox()]
  const c = [checkbox()]
  const visible = [c, a, b]
  const state = useCheckboxSelection()
  state.start(visible, 0, 0)
  visible.reverse()
  state.extend(2, 0)
  assert.deepEqual([...state.selected.value], [c[0], a[0], b[0]])
  assert.ok(!state.selected.value.has(hidden[0]))
  state.extend(1, 0)
  assert.deepEqual([...state.selected.value], [c[0], a[0]])
  state.stop()
  state.extend(2, 0)
  assert.equal(state.selected.value.size, 2)
  state.clear()
  assert.equal(state.selected.value.size, 0)
})
