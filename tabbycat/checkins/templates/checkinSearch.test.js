import assert from 'node:assert/strict'
import test from 'node:test'
import { normaliseSearch, searchGroups } from './checkinSearch.js'

test('matches case and canonically equivalent Unicode as literal text', () => {
  const entity = { name: 'José O’Neill' }
  assert.deepEqual(searchGroups({ A: [entity] }, normaliseSearch('  JOSÉ  ')), [['A', [entity]]])
  assert.deepEqual(searchGroups({ A: [entity] }, normaliseSearch('Jose\u0301')), [['A', [entity]]])
  assert.deepEqual(searchGroups({ A: [entity] }, normaliseSearch('neill jos')), [])
  assert.deepEqual(searchGroups({ A: [{ name: 'A.*B' }] }, '.*'), [['A', [{ name: 'A.*B' }]]])
})

test('preserves group and entity order and removes only nonmatches', () => {
  const alice = { name: 'Alice' }
  const brown = { name: 'Brown Alice' }
  const bob = { name: 'Bob' }
  const groups = { Oxford: [{ name: 'Alice Brown' }], Empty: [bob], York: [brown, alice] }
  assert.deepEqual(searchGroups(groups, 'alice'), [['Oxford', groups.Oxford], ['York', [brown, alice]]])
  assert.deepEqual(groups.Empty, [bob])
  assert.deepEqual(searchGroups(groups, ''), Object.entries(groups))
  assert.deepEqual(searchGroups(groups, 'nobody'), [])
})

test('filters displayed names and preserves live objects for bulk check-in', () => {
  const entity = { name: 'Team 001', team_real_name: 'Secret', institution: { name: 'Private' }, status: false }
  assert.deepEqual(searchGroups({ Teams: [entity] }, 'secret'), [])
  assert.deepEqual(searchGroups({ Teams: [entity] }, 'private'), [])
  assert.equal(searchGroups({ Teams: [entity] }, '001')[0][1][0], entity)
  entity.status = { time: '2026-10-03T10:00:00Z' }
  assert.equal(searchGroups({ Teams: [entity] }, '001')[0][1][0].status, entity.status)
})
