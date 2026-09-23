import { computed, ref, watch } from 'vue'
import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'

export function useModalAction ({ modalRef = null, contextOfAction = null } = {}) {
  const store = useDragAndDropStore()

  const modal = modalRef ?? ref(null)

  const action = computed(() => {
    if (contextOfAction && typeof contextOfAction === 'object' && 'value' in contextOfAction) {
      return contextOfAction.value
    }
    return contextOfAction
  })

  const loading = computed(() => store.loadingState)

  const setLoading = (value) => {
    store.setLoadingState(value)
  }

  const resetModal = () => {
    if (modal.value) {
      window.$?.(modal.value).modal('hide')
    }
  }

  const performWSAction = (settings = null) => {
    setLoading(true)
    store.wsBridge?.send({
      action: action.value,
      settings: settings,
    })
  }

  watch(loading, (newValue, oldValue) => {
    if (newValue === false && oldValue === true) {
      resetModal()
    }
  })

  return {
    modal,
    loading,
    setLoading,
    resetModal,
    performWSAction,
  }
}
