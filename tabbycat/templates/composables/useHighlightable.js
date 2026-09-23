import { computed } from 'vue'
import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'

export function useHighlightable ({ highlightData }) {
  const store = useDragAndDropStore()

  const getCSSForOverlapping = (highlightKey, highlightType) => {
    const data = highlightData.value
    if (
      typeof data === 'object' &&
      data &&
      highlightKey in data &&
      highlightType in store.highlights
    ) {
      let classes = []
      const highlightCategories = Object.keys(store.highlights[highlightType].options)
      for (const category of data[highlightKey]) {
        let matchingCategory = []
        if (typeof category === 'object') {
          matchingCategory = highlightCategories.filter(
            bc => store.highlights[highlightType].options[bc].pk === category.id)
        } else {
          matchingCategory = highlightCategories.filter(
            bc => store.highlights[highlightType].options[bc].pk === category)
        }
        if (matchingCategory.length > 0) {
          classes += ' ' + store.highlights[highlightType].options[matchingCategory[0]].css
        }
      }
      return classes
    }
    return ''
  }

  const getCSSForOrder = (highlightKey, highlightType) => {
    const data = highlightData.value
    if (data && typeof data === 'object') {
      if (highlightKey in data) {
        const orderedCategories = Object.keys(store.highlights[highlightType].options)
        for (const category of orderedCategories) {
          if (data[highlightKey] >= store.highlights[highlightType].options[category].fields.cutoff) {
            return store.highlights[highlightType].options[category].css
          }
        }
      }
    }
    return ''
  }

  const activeClass = computed(() => {
    const currentKey = Object.keys(store.highlights).filter(key => store.highlights[key].active)
    if (currentKey.length > 0) {
      return currentKey + '-display'
    }
    return ''
  })

  const breakClass = computed(() => getCSSForOverlapping('break_categories', 'break'))
  const categoryClass = computed(() => getCSSForOverlapping('categories', 'category'))

  const genderClass = computed(() => {
    const data = highlightData.value
    if (data && typeof data === 'object') {
      if ('gender' in data) {
        return ` gender-${data.gender}`
      }
    }
    if (data && typeof data === 'object') {
      if ('speakers' in data) {
        let classString = ''
        const men = data.speakers.filter(s => s.gender === 'M')
        const notmen = data.speakers.filter(s => s.gender === 'F' || s.gender === 'O')
        classString += `gender-men-${men.length} gender-notmen-${notmen.length}`
        return classString
      }
    }
    return ''
  })

  const regionClass = computed(() => {
    const data = highlightData.value
    if (data && typeof data === 'object') {
      if ('institution' in data) {
        const itemsInstitutionID = data.institution
        if (itemsInstitutionID && 'region' in store.highlights) {
          if (itemsInstitutionID in store.allInstitutions) {
            const itemsInstitution = store.allInstitutions[itemsInstitutionID]
            const itemsRegion = store.highlights.region.options[itemsInstitution.region]
            if (itemsRegion) {
              return store.highlights.region.options[itemsInstitution.region].css
            }
          }
        }
      }
    }
    return ''
  })

  const rankClass = computed(() => getCSSForOrder('score', 'rank'))
  const priorityClass = computed(() => getCSSForOrder('priority', 'priority'))

  const highlightsCSS = computed(() => {
    return [
      activeClass.value,
      breakClass.value,
      genderClass.value,
      regionClass.value,
      rankClass.value,
      priorityClass.value,
      categoryClass.value,
    ].join(' ')
  })

  return {
    highlightsCSS,
  }
}
