export const normaliseSearch = value => value.toLowerCase().normalize('NFD')
  .replace(/\p{M}/gu, '').replace(/[^\p{L}\p{N}]+/gu, ' ').trim()

export function scoreName (name, query) {
  if (!query || name === query) return 0
  if (name.startsWith(query)) return 1
  const tokens = query.split(' ')
  const words = name.split(' ')
  if (tokens.every(token => words.some(word => word.startsWith(token)))) return 2
  if (tokens.every(token => name.includes(token))) return 3
  return null
}

// Filter before rendering so bulk check-in actions only receive visible entities.
export function searchGroups (groups, query) {
  if (!query) return Object.entries(groups)
  return Object.entries(groups).map(([label, entities]) => {
    const matches = entities.map(entity => ({ entity, score: scoreName(normaliseSearch(entity.name), query) }))
      .filter(match => match.score !== null).sort((a, b) => a.score - b.score)
    return { label, matches }
  }).filter(group => group.matches.length)
    .sort((a, b) => a.matches[0].score - b.matches[0].score)
    .map(group => [group.label, group.matches.map(match => match.entity)])
}

// Keep offsets into original text, including accents and astral Unicode characters.
// Render these segments through Vue interpolation, never HTML from names or queries.
export function highlightName (name, query) {
  if (!query) return [{ text: name, match: false }]
  let folded = ''
  const offsets = []
  let offset = 0
  for (const character of name) {
    const value = character.toLowerCase().normalize('NFD').replace(/\p{M}/gu, '')
    if (!value && offsets.length) offsets[offsets.length - 1].end = offset + character.length
    for (let i = 0; i < value.length; i++) offsets.push({ start: offset, end: offset + character.length })
    folded += value
    offset += character.length
  }
  const highlighted = Array(name.length).fill(false)
  for (const token of query.split(' ')) {
    let start = folded.indexOf(token)
    while (start !== -1) {
      highlighted.fill(true, offsets[start].start, offsets[start + token.length - 1].end)
      start = folded.indexOf(token, start + 1)
    }
  }
  const parts = []
  for (let start = 0; start < name.length;) {
    let end = start + 1
    while (end < name.length && highlighted[end] === highlighted[start]) end++
    parts.push({ text: name.slice(start, end), match: highlighted[start] })
    start = end
  }
  return parts
}
