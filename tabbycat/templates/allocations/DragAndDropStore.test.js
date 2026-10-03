import assert from 'node:assert/strict'
import test from 'node:test'
import { createPinia, setActivePinia } from 'pinia'
import { useDragAndDropStore } from './DragAndDropStore.js'

const setup = () => {
  setActivePinia(createPinia())
  return useDragAndDropStore()
}

const item = { item: 7, assignment: 1, position: 'C' }
const destination = { assignment: 2, position: 'P' }

test('places in either selection order exactly once and clears the selection', () => {
  for (const itemFirst of [true, false]) {
    const store = setup()
    const moves = []
    const selectItem = () => store.selectAllocationItem(item)
    const selectTarget = () => store.selectAllocationTarget(destination, (...args) => moves.push(args))
    const first = itemFirst ? selectItem : selectTarget
    const second = itemFirst ? selectTarget : selectItem
    first()
    assert.equal(moves.length, 0)
    second()
    assert.deepEqual(moves, [[item, destination]])
    assert.equal(store.selectedAllocationItem, null)
    assert.equal(store.selectedAllocationTarget, null)
  }
})

test('tapping the same item or destination again deselects it', () => {
  const store = setup()
  store.selectAllocationItem(item)
  store.selectAllocationItem({ ...item })
  assert.equal(store.selectedAllocationItem, null)
  store.selectAllocationTarget(destination, () => assert.fail('Unexpected move'))
  store.selectAllocationTarget({ ...destination }, () => assert.fail('Unexpected move'))
  assert.equal(store.selectedAllocationTarget, null)
})

test('replacing a selection uses the latest item or destination', () => {
  const store = setup()
  const replacement = { ...item, item: 8 }
  store.selectAllocationItem(item)
  store.selectAllocationItem(replacement)
  store.selectAllocationTarget(destination, (payload) => assert.deepEqual(payload, replacement))
  store.selectAllocationTarget({ assignment: 3, position: 'C' }, () => assert.fail('Old destination'))
  store.selectAllocationTarget(destination, (_, context) => assert.deepEqual(context, destination))
  store.selectAllocationItem(item)
})

test('placing in the source slot is a no-op, including unallocated items', () => {
  for (const payload of [item, { item: 7, assignment: null, position: null }, { item: 7, assignment: 1 }]) {
    const store = setup()
    store.selectAllocationItem(payload)
    store.selectAllocationTarget({ assignment: payload.assignment, position: payload.position }, () => assert.fail('Self move'))
    assert.equal(store.selectedAllocationItem, null)
    assert.equal(store.selectedAllocationTarget, null)
  }
})

test('the unallocated pool can be used as a destination', () => {
  const store = setup()
  const pool = { assignment: null, position: null }
  let moved = false
  store.selectAllocationTarget(pool, (payload, context) => {
    moved = true
    assert.deepEqual(payload, item)
    assert.deepEqual(context, pool)
  })
  store.selectAllocationItem(item)
  assert.equal(moved, true)
})

test('cancel, remote changes, loading and sharding discard pending selections', () => {
  for (const clear of [
    store => store.clearAllocationSelection(),
    store => store.setDebateOrPanelAttributes([{ id: 1, venue: 4 }]),
    store => store.setLoadingState(true),
    store => store.setSharding({ option: 'index', value: 1 }),
  ]) {
    const store = setup()
    store.selectAllocationItem(item)
    clear(store)
    assert.equal(store.selectedAllocationItem, null)
    store.selectAllocationTarget(destination, () => {})
    clear(store)
    assert.equal(store.selectedAllocationTarget, null)
  }
})
