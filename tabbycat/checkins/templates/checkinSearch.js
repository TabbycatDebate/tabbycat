import _ from 'lodash'
import { caseFold } from 'unicode-case-folding'

const segments = value => new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(value)
const fold = (value, unicode) => unicode ? caseFold(value).normalize('NFD') : value.toLowerCase()
const clean = (value, unicode) => unicode ? value.normalize('NFD') : _.deburr(value).split('\'').join('').split('’').join('')
const searchForms = value => [_.lowerCase(value), fold(value.normalize('NFD'), true)]

function closeWord (query, word) {
  const a = [...query]
  const b = [...word]
  if (a.length < 4 || !Number.isNaN(Number(query)) || Math.abs(a.length - b.length) > 1) return false
  let edits = 0
  for (let i = 0, j = 0; i < a.length || j < b.length;) {
    if (a[i] === b[j]) { i++; j++ } else {
      if (edits++) return false
      if (a.length >= b.length) i++
      if (a.length <= b.length) j++
    }
  }
  return true
}

// Query words are alternatives; retain phrase matches and include one-edit word matches.
function matchRanges (text, query) {
  if (!query) return []
  const tokens = _.words(query)
  const matches = []
  for (const pattern of new Set([query, ...tokens])) {
    for (let index = text.indexOf(pattern); index !== -1; index = text.indexOf(pattern, index + 1)) {
      matches.push([index, index + pattern.length])
    }
  }
  let cursor = 0
  for (const word of _.words(text)) {
    const index = text.indexOf(word, cursor)
    cursor = index + word.length
    if (tokens.some(token => !word.includes(token) && closeWord(token, word))) matches.push([index, cursor])
  }
  return matches
}

export function normaliseSearch (value) {
  const input = value.trim()
  if ((Intl.Segmenter ? [...segments(input)] : [...input]).length < 2) return null
  return searchForms(input)
}

const matchesSearch = (value, query) => query && searchForms(value).some((text, mode) =>
  !query[mode] || matchRanges(text, query[mode]).length,
)

export function institutionMatches (entity, query, unaffiliated = 'Unaffiliated') {
  const institution = entity.institution === null ? { name: unaffiliated } : entity.institution
  return [institution?.code, institution?.name].some(value => value && matchesSearch(value, query))
}

// Keep Lodash matches and add canonical Unicode matches, preserving group order and live entities.
export function searchGroups (groups, query, unaffiliated = 'Unaffiliated') {
  const entries = Object.entries(groups)
  if (!query) return entries
  return entries.map(([label, entities]) => [label, entities.filter(entity =>
    matchesSearch(entity.name, query) || institutionMatches(entity, query, unaffiliated),
  )]).filter(([, entities]) => entities.length)
}

export function highlightName (name, query) {
  if (!query || !Intl.Segmenter) return [{ text: name, match: false }]
  const graphemes = [...segments(name)]
  const highlighted = Array(name.length).fill(false)
  for (const unicode of [false, true]) {
    const source = clean(name, unicode)
    const sourceOffsets = []
    for (const { segment, index } of graphemes) {
      sourceOffsets.push(...Array(clean(segment, unicode).length).fill([index, index + segment.length]))
    }
    const offsets = []
    let cursor = 0
    // Normalize the whole name (Unicode) or whole words (Lodash); offsets only map back to display text.
    const text = (unicode ? [source] : _.words(source)).map(word => {
      let index = source.indexOf(word, cursor)
      cursor = index + word.length
      for (const char of word) {
        offsets.push(...Array(fold(char, unicode).length).fill(sourceOffsets[index]))
        index += char.length
      }
      offsets.push(null) // Space inserted between words, rather than a displayed character.
      return fold(word, unicode)
    }).join(' ')
    for (const [start, end] of matchRanges(text, query[Number(unicode)])) {
      highlighted.fill(true, offsets[start][0], offsets[end - 1][1])
    }
  }
  const parts = []
  for (const { segment, index } of graphemes) {
    const match = highlighted[index]
    if (parts.length && parts[parts.length - 1].match === match) parts[parts.length - 1].text += segment
    else parts.push({ text: segment, match })
  }
  return parts
}
