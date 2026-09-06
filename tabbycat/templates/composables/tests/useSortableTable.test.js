import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ref } from 'vue'
import { useSortableTable } from '../useSortableTable.js'

function table (rows, defaults = {}) {
  const sortableData = ref(rows)
  const state = useSortableTable({
    headers: ref([{ key: 'name' }, { key: 'score' }]),
    sortableData,
    getSortableProperty: (row, index) => row[index].text,
    ...defaults,
  })
  return { ...state, sortableData }
}

const rows = () => ['Alpha', 'Charlie', 'Bravo'].map(name => [{ text: name }, { text: 10 }])
const names = state => state.dataOrderedByKey.value.map(row => row[0].text)

test('changing columns preserves the previous order within ties', () => {
  const state = table(rows())
  state.updateSorting('name')
  assert.deepEqual(names(state), ['Charlie', 'Bravo', 'Alpha'])
  state.updateSorting('score')
  assert.deepEqual(names(state), ['Charlie', 'Bravo', 'Alpha'])
  state.updateSorting('score')
  assert.deepEqual(names(state), ['Charlie', 'Bravo', 'Alpha'])
  assert.deepEqual(state.sortableData.value, rows())
})

test('descending ties retain their input order without an earlier sort', () => {
  const state = table(rows(), { defaultSortKey: 'score', defaultSortOrder: 'desc' })
  assert.deepEqual(names(state), ['Alpha', 'Charlie', 'Bravo'])
})

test('default sorting participates in subsequent tie breaking', () => {
  const state = table(rows(), { defaultSortKey: 'name', defaultSortOrder: 'asc' })
  state.updateSorting('score')
  assert.deepEqual(names(state), ['Alpha', 'Bravo', 'Charlie'])
})

test('new rows use the current sort history', () => {
  const state = table(rows())
  state.updateSorting('name')
  state.updateSorting('score')
  state.sortableData.value = [...rows(), [{ text: 'Delta' }, { text: 10 }]]
  assert.deepEqual(names(state), ['Delta', 'Charlie', 'Bravo', 'Alpha'])
})

test('the latest column and direction outrank earlier sorts', () => {
  const state = table([
    [{ text: 'Alpha' }, { text: 20 }],
    [{ text: 'Charlie' }, { text: 10 }],
    [{ text: 'Bravo' }, { text: 20 }],
  ])
  state.updateSorting('name')
  state.updateSorting('score')
  assert.deepEqual(names(state), ['Bravo', 'Alpha', 'Charlie'])
  state.updateSorting('score')
  assert.deepEqual(names(state), ['Charlie', 'Bravo', 'Alpha'])
  state.updateSorting('name')
  state.updateSorting('name')
  assert.deepEqual(names(state), ['Alpha', 'Bravo', 'Charlie'])
})
