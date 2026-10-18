import assert from 'node:assert/strict'
import test from 'node:test'
import _ from 'lodash'
import { highlightName, institutionMatches, normaliseSearch, searchGroups } from './checkinSearch.js'

test('starts after two input graphemes, before normalization can expand them', () => {
  const groups = { A: [{ name: 'Alice' }], Empty: [] }
  for (const input of ['', ' ', 'a', 'ß', 'e\u0301', '𐐀', '👩‍💻']) {
    const query = normaliseSearch(input)
    assert.equal(query, null)
    assert.deepEqual(searchGroups(groups, query), Object.entries(groups))
    assert.deepEqual(highlightName('Alice', query), [{ text: 'Alice', match: false }])
  }
  assert.deepEqual(searchGroups(groups, normaliseSearch('zz')), [])
  assert.deepEqual(searchGroups(groups, normaliseSearch(' al ')), [['A', groups.A]])
  assert.deepEqual(searchGroups(groups, normaliseSearch('...')), [['A', groups.A]])
})

test('preserves group order, entity identity and displayed-name scope', () => {
  const alice = { name: 'Alice', team_real_name: 'Secret', institution: { name: 'Private' } }
  const brown = { name: 'Brown Alice' }
  const groups = { Oxford: [{ name: 'Alice Brown' }], Empty: [{ name: 'Bob' }], York: [brown, alice] }
  assert.deepEqual(searchGroups(groups, normaliseSearch('alice')), [['Oxford', groups.Oxford], ['York', [brown, alice]]])
  assert.deepEqual(searchGroups(groups, normaliseSearch('brown nobody')), [['Oxford', groups.Oxford], ['York', [brown]]])
  assert.equal(searchGroups(groups, normaliseSearch('alice'))[1][1][1], alice)
  for (const query of ['secret', 'nobody']) assert.deepEqual(searchGroups(groups, normaliseSearch(query)), [])
  assert.equal(groups.Empty.length, 1)
})

test('matches institution names and codes while respecting displayed affiliations', () => {
  const alice = { name: 'Alice', institution: { code: 'OXF', name: 'Oxford University' } }
  const bob = { name: 'Bob', institution: { code: 'OXF', name: 'Oxford University' } }
  const carol = { name: 'Carol', institution: null }
  const groups = { A: [alice], B: [bob, carol] }
  for (const input of ['oxf', 'Oxford', 'oxfrd']) {
    const query = normaliseSearch(input)
    assert.deepEqual(searchGroups(groups, query), [['A', [alice]], ['B', [bob]]])
    assert.equal(institutionMatches(alice, query), true)
    assert.equal(institutionMatches(carol, query), false)
  }
  assert.equal(searchGroups(groups, normaliseSearch('oxf'))[0][1][0], alice)
  assert.equal(institutionMatches(alice, normaliseSearch('alice')), false)
  assert.equal(institutionMatches(alice, normaliseSearch('o')), false)
  for (const input of ['unaffiliated', 'unaf', 'unafiliated']) {
    const query = normaliseSearch(input)
    assert.deepEqual(searchGroups(groups, query), [['B', [carol]]])
    assert.equal(institutionMatches(carol, query), true)
    assert.equal(institutionMatches(alice, query), false)
    assert.equal(institutionMatches({ name: 'Room 001' }, query), false)
  }
  const translated = normaliseSearch('sans affiliation')
  assert.deepEqual(searchGroups(groups, translated, 'Sans affiliation'), [['B', [carol]]])
  assert.equal(institutionMatches(carol, translated, 'Sans affiliation'), true)
  const anonymous = { name: 'Team 001', institution: { code: 'Anonymous (due to team codes)', name: 'Anon' } }
  assert.deepEqual(searchGroups({ A: [anonymous] }, normaliseSearch('Oxford')), [])
})

test('retains Lodash matches and adds Unicode equivalents with intact highlighting', () => {
  for (const [name, query] of [
    ['José Smith', 'Jose Smith'], ['Alice-Brown', 'Alice Brown'], ['AliceBrown', 'Alice Brown'],
    ['O’Connor', 'o connor'], ['A.*B.*C', 'a b c'], ['FOOBar', 'foo bar'],
    ['Straße', 'STRASSE'], ['STRAẞE', 'strasse'], ['Jose\u0301', 'JOSÉ'],
    ['hộx', 'ho\u0302\u0323x'], ['ho\u0302\u0323x', 'hộx'],
    ['q\u0307\u0323x', 'q\u0323\u0307x'], ['a\u0315\u0300x', 'àx'],
    ['ΟΣ', 'οσ'], ['Σx', 'ςx'], ['𐐀lice', '𐐨lice'], ['ﬃ', 'FFI'],
  ]) {
    const entity = { name: `${name} / 9999` }
    const normalised = normaliseSearch(query)
    assert.deepEqual(searchGroups({ A: [entity] }, normalised), [['A', [entity]]], `${name} / ${query}`)
    assert.deepEqual(highlightName(entity.name, normalised), [
      { text: name, match: true }, { text: ' / 9999', match: false },
    ], `${name} / ${query}`)
  }
})

test('maps overlaps, word boundaries and case expansions back to original text', () => {
  for (const [name, query, expected] of [
    ['banana', 'ana', [['b', false], ['anana', true]]],
    ['ΟΣΟΣ', 'σοσ', [['Ο', false], ['ΣΟΣ', true]]],
    ['xStraßez', 'SS', [['xStra', false], ['ß', true], ['ez', false]]],
    ['fooBARBaz', 'baz', [['fooBAR', false], ['Baz', true]]],
    ['AliceBrown', 'ice br', [['Al', false], ['iceBr', true], ['own', false]]],
    ['hi 👩‍💻!', 'hi 👩‍💻', [['hi 👩‍💻', true], ['!', false]]],
  ]) assert.deepEqual(highlightName(name, normaliseSearch(query)), expected.map(([text, match]) => ({ text, match })))
})

test('matches any query word with one edit, without number aliases or short-word typos', () => {
  const entity = { name: 'three people' }
  for (const [query, expected] of [
    ['3 peope', [['three ', false], ['people', true]]],
    ['threw', [['three', true], [' people', false]]],
    ['absent peoples', [['three ', false], ['people', true]]],
    ['peple', [['three ', false], ['people', true]]],
    ['three absent', [['three', true], [' people', false]]],
  ]) {
    const normalised = normaliseSearch(query)
    assert.deepEqual(searchGroups({ A: [entity] }, normalised), [['A', [entity]]], query)
    assert.deepEqual(highlightName(entity.name, normalised), expected.map(([text, match]) => ({ text, match })), query)
  }
  for (const query of ['03', '3 absent', 'thrxw', 'tx']) {
    assert.deepEqual(searchGroups({ A: [entity] }, normaliseSearch(query)), [], query)
    assert.deepEqual(highlightName(entity.name, normaliseSearch(query)), [{ text: entity.name, match: false }], query)
  }
  assert.deepEqual(searchGroups({ A: [{ name: 'Room 1234' }] }, normaliseSearch('1235')), [])
})

test('includes every Lodash result for representative word and Unicode boundaries', () => {
  const names = ['José Smith', 'hộ Nguyen', 'AliceBrown', 'fooBARBaz', 'Straße', 'ΟΣΟΣ', 'O’Connor', 'A.*B.*C', 'Room 001']
  const queries = ['jose smith', 'hộ', 'alice brown', 'bar baz', 'strasse', 'οσος', 'o connor', 'a b c', '001', '...']
  for (const name of names) for (const query of queries) {
    if (_.lowerCase(name).includes(_.lowerCase(query))) {
      assert.equal(searchGroups({ A: [{ name }] }, normaliseSearch(query)).length, 1, `${name} / ${query}`)
    }
  }
})

test('preserves unmatched text and falls back without grapheme segmentation', t => {
  const name = '<img src=x onerror=alert(1)>'
  assert.equal(highlightName(name, normaliseSearch('img')).map(part => part.text).join(''), name)
  assert.deepEqual(highlightName('Alice', normaliseSearch('zz')), [{ text: 'Alice', match: false }])
  const original = Intl.Segmenter
  t.after(() => { Intl.Segmenter = original })
  Intl.Segmenter = undefined
  assert.deepEqual(highlightName('José', normaliseSearch('jose')), [{ text: 'José', match: false }])
  assert.equal(searchGroups({ A: [{ name: 'José' }] }, normaliseSearch('jose')).length, 1)
})
