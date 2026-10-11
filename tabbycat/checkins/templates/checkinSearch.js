export const normaliseSearch = value => value.toLowerCase().normalize('NFD').trim()

// Filter before rendering so bulk check-in actions only receive visible entities.
export function searchGroups (groups, query) {
  if (!query) return Object.entries(groups)
  return Object.entries(groups)
    .map(([label, entities]) => [label, entities.filter(entity => normaliseSearch(entity.name).includes(query))])
    .filter(([, entities]) => entities.length)
}

// Map normalized matches back to original text; Vue renders each part as text.
export function highlightName (name, query) {
  if (!query) return [{ text: name, match: false }]
  const folded = name.toLowerCase().normalize('NFD')
  const offsets = []
  let offset = 0
  for (const character of name) {
    const value = character.toLowerCase().normalize('NFD')
    for (let i = 0; i < value.length; i++) offsets.push({ start: offset, end: offset + character.length })
    offset += character.length
  }
  const highlighted = Array(name.length).fill(false)
  let match = folded.indexOf(query)
  while (match !== -1) {
    highlighted.fill(true, offsets[match].start, offsets[match + query.length - 1].end)
    match = folded.indexOf(query, match + query.length)
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
