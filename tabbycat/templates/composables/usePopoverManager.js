import { ref } from 'vue'

const activePopoverUid = ref(null)

export function usePopoverManager() {
  const registerPopover = (uid) => {
    activePopoverUid.value = uid
  }

  const isActivePopover = (uid) => {
    return activePopoverUid.value === uid
  }

  const shouldHidePopover = (uid) => {
    return activePopoverUid.value !== null && activePopoverUid.value !== uid
  }

  return {
    registerPopover,
    isActivePopover,
    shouldHidePopover,
    activePopoverUid,
  }
}
