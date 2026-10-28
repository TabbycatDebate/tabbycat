import assert from 'node:assert/strict'
import { test } from 'node:test'
import { replySpeakerOptions } from './replySpeakerOptions.js'

const options = [
  { text: 'Third Speaker', value: 'third' },
  { text: 'First Speaker', value: 'first' },
  { text: 'Second Speaker', value: 'second' },
]

test('excludes the selected third substantive speaker from a WSDC reply list', () => {
  assert.deepEqual(
    replySpeakerOptions(options, true, true, 'third').map(option => option.value),
    ['first', 'second'],
  )
})

test('updates exclusion when the third substantive speaker changes', () => {
  assert.deepEqual(
    replySpeakerOptions(options, true, true, 'third').map(option => option.value),
    ['first', 'second'],
  )
  assert.deepEqual(
    replySpeakerOptions(options, true, true, 'first').map(option => option.value),
    ['second', 'third'],
  )
})

test('preserves reply options when the restriction is disabled', () => {
  assert.deepEqual(
    replySpeakerOptions(options, false, true, 'third').map(option => option.value),
    ['first', 'second', 'third'],
  )
})
