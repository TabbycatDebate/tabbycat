import assert from 'node:assert/strict'
import test from 'node:test'
import { highlightName, normaliseSearch, searchGroups } from './checkinSearch.js'

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

test('highlights canonical Unicode matches without changing original text', () => {
  for (const name of ['José Smith', 'Jose\u0301 Smith']) {
    const parts = highlightName(name, normaliseSearch('JOSÉ'))
    assert.equal(parts.map(part => part.text).join(''), name)
    assert.equal(parts[0].text, name.slice(0, name.indexOf(' ')))
    assert.equal(parts[0].match, true)
  }
  assert.deepEqual(highlightName('ΟΣ', normaliseSearch('ος')), [{ text: 'ΟΣ', match: true }])
  assert.deepEqual(highlightName('𐐀lice Smith', normaliseSearch('𐐀lice')), [
    { text: '𐐀lice', match: true }, { text: ' Smith', match: false },
  ])
})

test('highlights repeated literal matches and preserves HTML as text', () => {
  assert.deepEqual(highlightName('A.*B.*C', '.*'), [
    { text: 'A', match: false }, { text: '.*', match: true },
    { text: 'B', match: false }, { text: '.*', match: true }, { text: 'C', match: false },
  ])
  const name = '<img src=x onerror=alert(1)>'
  assert.equal(highlightName(name, 'img').map(part => part.text).join(''), name)
  assert.deepEqual(highlightName('Alice', ''), [{ text: 'Alice', match: false }])
  assert.deepEqual(highlightName('Alice', 'bob'), [{ text: 'Alice', match: false }])
})
