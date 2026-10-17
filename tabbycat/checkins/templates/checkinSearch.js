export const normaliseSearch = value => value.toLowerCase().normalize('NFD').trim()

// Filter before rendering so bulk check-in actions only receive visible entities.
export function searchGroups (groups, query) {
  if (!query) return Object.entries(groups)
  return Object.entries(groups)
    .map(([label, entities]) => [label, entities.filter(entity => normaliseSearch(entity.name).includes(query))])
    .filter(([, entities]) => entities.length)
}
