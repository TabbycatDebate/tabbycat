import { computed } from 'vue'
import feather from 'feather-icons'

export function useFeatherIcon (icon) {
  const resolved = computed(() => {
    if (icon && typeof icon === 'object' && 'value' in icon) {
      return icon.value
    }
    return icon
  })

  const getFeatherIcon = computed(() => {
    if (!resolved.value) {
      return null
    }
    const item = feather.icons[resolved.value]
    return item ? item.toSvg() : null
  })

  return {
    getFeatherIcon,
  }
}
