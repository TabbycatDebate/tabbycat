import assert from 'node:assert/strict'
import test from 'node:test'
import { highlightName, normaliseSearch, scoreName, searchGroups } from './checkinSearch.js'

test('matches accents, punctuation, case and words in any order', () => {
  assert.equal(normaliseSearch('  JOSÉ—O’Neill  '), 'jose o neill')
  assert.equal(scoreName(normaliseSearch('José O’Neill'), normaliseSearch('neill jos')), 2)
  assert.equal(scoreName('alice', 'bob'), null)
  assert.equal(scoreName('北京 大学', '北京'), 1)
})

test('ranks exact, prefix, word-prefix and substring matches', () => {
  const names = ['Malice', 'Smith Alice', 'Alice Smith', 'Alice']
  const groups = { A: names.map(name => ({ name })) }
  assert.deepEqual(searchGroups(groups, 'alice')[0][1].map(entity => entity.name), [
    'Alice', 'Alice Smith', 'Smith Alice', 'Malice',
  ])
})

test('removes empty groups and keeps only matching entities for bulk actions', () => {
  const alice = { name: 'Alice', identifier: ['1'] }
  const bob = { name: 'Bob', identifier: ['2'] }
  const groups = { First: [bob], Second: [bob, alice] }
  assert.deepEqual(searchGroups(groups, 'alice'), [['Second', [alice]]])
  assert.deepEqual(groups.Second, [bob, alice])
  assert.deepEqual(searchGroups(groups, ''), Object.entries(groups))
  assert.deepEqual(searchGroups(groups, 'nobody'), [])
})

test('searches displayed names only, ignoring hidden team and institution names', () => {
  const entity = { name: 'Team 001', team_real_name: 'Secret', institution: { name: 'Private' } }
  assert.deepEqual(searchGroups({ Teams: [entity] }, 'secret'), [])
  assert.deepEqual(searchGroups({ Teams: [entity] }, 'private'), [])
  assert.deepEqual(searchGroups({ Teams: [entity] }, '001'), [['Teams', [entity]]])
})

test('retains current objects and statuses after live check-in updates', () => {
  const absent = { name: 'Alice', status: false }
  const present = { ...absent, status: { time: '2026-10-03T10:00:00Z' } }
  assert.equal(searchGroups({ A: [absent] }, 'alice')[0][1][0].status, false)
  assert.equal(searchGroups({ A: [present] }, 'alice')[0][1][0], present)
})

test('highlights accented names while preserving original text', () => {
  assert.deepEqual(highlightName('José Smith', 'jose'), [
    { text: 'José', match: true }, { text: ' Smith', match: false },
  ])
  const name = 'Jose\u0301 𐐀lice'
  assert.equal(highlightName(name, 'jose')[0].text, 'Jose\u0301')
  const parts = highlightName(name, normaliseSearch('𐐀lice'))
  assert.equal(parts.map(part => part.text).join(''), name)
  assert.equal(parts.find(part => part.match).text, '𐐀lice')
})

test('treats HTML and regex metacharacters as plain text', () => {
  const name = '<img src=x onerror=alert(1)>'
  const parts = highlightName(name, 'img')
  assert.equal(parts.map(part => part.text).join(''), name)
  assert.deepEqual(highlightName('A.*B', '.*'), [
    { text: 'A', match: false }, { text: '.*', match: true }, { text: 'B', match: false },
  ])
  assert.deepEqual(highlightName('Alice', ''), [{ text: 'Alice', match: false }])
})
