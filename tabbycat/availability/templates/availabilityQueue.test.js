import assert from 'node:assert/strict'
import test from 'node:test'
import { setTimeout as delay } from 'node:timers/promises'
import { createAvailabilityQueue } from './availabilityQueue.js'

test('batches drag edits by round and sends the latest state of each checkbox', async () => {
  const cells = [
    { id: 1, updateURL: '/round/1', checked: false },
    { id: 2, updateURL: '/round/1', checked: false },
    { id: 1, updateURL: '/round/2', checked: false },
  ]
  const saves = []
  const queue = createAvailabilityQueue(cells, async (...args) => saves.push(args), () => {}, () => {})
  for (const cell of cells) {
    cell.checked = true
    queue.enqueue(cell)
  }
  cells[0].checked = false
  queue.enqueue(cells[0])
  assert.equal(await queue.whenIdle(), true)
  assert.deepEqual(saves, [
    ['/round/1', { 1: false, 2: true }],
    ['/round/2', { 1: true }],
  ])
})

test('serializes edits made while a save is in flight', async () => {
  const cell = { id: 1, updateURL: '/round/1', checked: false }
  const saves = []
  let finishSave
  let saved = 0
  const queue = createAvailabilityQueue([cell], (...args) => {
    saves.push(args)
    return new Promise(resolve => { finishSave = resolve })
  }, () => {}, (success) => { if (success) saved += 1 })
  cell.checked = true
  queue.enqueue(cell)
  const settled = queue.whenIdle()
  await delay(80)
  cell.checked = false
  queue.enqueue(cell)
  assert.equal(saves.length, 1)
  assert.equal(queue.whenIdle(), settled)
  finishSave()
  await delay(0)
  assert.deepEqual(saves, [['/round/1', { 1: true }], ['/round/1', { 1: false }]])
  assert.equal(saved, 0)
  finishSave()
  assert.equal(await settled, true)
  assert.equal(saved, 1)
  assert.equal(queue.whenIdle(), null)
})

test('restores failed cells and keeps newer queued edits', async () => {
  const first = { id: 1, updateURL: '/round/1', checked: true }
  const second = { id: 2, updateURL: '/round/1', checked: false }
  let failSave
  let calls = 0
  let saved = 0
  const queue = createAvailabilityQueue([first, second], () => {
    calls += 1
    if (calls === 1) return new Promise((resolve, reject) => { failSave = reject })
    return Promise.resolve()
  }, () => {}, (success) => { if (success) saved += 1 })
  first.checked = false
  second.checked = true
  queue.enqueue(first)
  queue.enqueue(second)
  const settled = queue.whenIdle()
  await delay(80)
  second.checked = false
  queue.enqueue(second)
  failSave(new Error('offline'))
  assert.equal(await settled, false)
  assert.equal(first.checked, true)
  assert.equal(second.checked, false)
  assert.equal(calls, 2)
  assert.equal(saved, 0)
})
