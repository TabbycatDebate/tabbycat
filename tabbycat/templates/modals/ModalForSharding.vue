<script setup>
import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'
import { useModalAction } from '../composables/useModalAction.js'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

defineProps({
  introText: String,
})

const { gettext } = useDjangoI18n()
const store = useDragAndDropStore()
const { sharding } = storeToRefs(store)

const modal = ref(null)
const { resetModal } = useModalAction({ modalRef: modal })

const splitOptions = [
  { label: 'Halves', value: 2 },
  { label: 'Thirds', value: 3 },
  { label: 'Quarters', value: 4 },
  { label: 'Fifths', value: 5 },
  { label: 'Sixths', value: 6 },
]
const mixOptions = ['Top-to-Bottom', 'Interleaved']
const sortOptions = ['Bracket', 'Importance']
const explanationText = `This helps allow this page to be edited across several computers as it
    guarantees that changes made in one shard wont affect the others. However, you need to
    ensure that each computer uses identical split/mix/sort settings and selects a different
    shard from the others`
const splitExplanation = `Top-to-Bottom mixing will sort the draw so the first shard contains the
    top-most brackets, priority, or liveness while the last shard contains the bottom-most
    brackets, priority, or liveness. In contrast, Interleave will distribute an even mix of each
    characteristic amongst each shard`

const index = computed(() => sharding.value.index)
const split = computed(() => sharding.value.split)
const mix = computed(() => sharding.value.mix)
const sort = computed(() => sharding.value.sort)

const shardOptions = computed(() => {
  if (split.value === 2) {
    return ['A', 'B']
  } else if (split.value === 3) {
    return ['A', 'B', 'C']
  } else if (split.value === 4) {
    return ['A', 'B', 'C', 'D']
  } else if (split.value === 5) {
    return ['A', 'B', 'C', 'D', 'E']
  } else if (split.value === 6) {
    return ['A', 'B', 'C', 'D', 'E', 'F']
  }
  return null
})

const setSharding = (payload) => {
  store.setSharding(payload)
}

const setState = (key, value) => {
  setSharding({ option: key, value: value })
}

const openShard = (shardIdentifier, selectedIndex) => {
  resetModal()
  setSharding({ option: 'index', value: selectedIndex })
  window.$?.fn?.showAlert?.('success', `Opened shard ${split.value} ${shardIdentifier}
                                 (sorted by ${mix.value} using ${sort.value})`)
}

const closeShard = () => {
  resetModal()
  setState('index', null)
  window.$?.fn?.showAlert?.('success', 'Closed shard')
}

const id = 'confirmShardModal'
</script>

<template>
  <div
    :id="id"
    ref="modal"
    class="modal fade"
    tabindex="-1"
    role="dialog"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-lg">
      @@
      <div class="modal-content">
        <div class="modal-body text-center p-4">
          <p class="lead">
            {{ introText }}
          </p>
          <p>{{ gettext(explanationText) }}</p>
          <p>{{ gettext(splitExplanation) }}</p>

          <div
            class="btn-group mb-4 btn-group-toggle"
            role="group"
          >
            <button
              disabled
              class="btn btn-outline-secondary"
            >
              {{ gettext('Shard Mix') }}
            </button>
            <button
              v-for="option in mixOptions"
              type="button"
              :class="['btn btn-outline-primary', mix === option ? 'active': '']"
              @click="setState('mix', option)"
            >
              {{ gettext(option) }}
            </button>
          </div>

          <div
            class="btn-group mb-4 btn-group-toggle"
            role="group"
          >
            <button
              disabled
              class="btn btn-outline-secondary"
            >
              {{ gettext('Shard Split') }}
            </button>
            <button
              v-for="option in splitOptions"
              type="button"
              :class="['btn btn-outline-primary', split === option.value ? 'active': '']"
              @click="setState('split', option.value)"
            >
              {{ gettext('In ' + option.label) }}
            </button>
          </div>

          <div
            class="btn-group mb-4 btn-group-toggle"
            role="group"
          >
            <button
              disabled
              class="btn btn-outline-secondary"
            >
              {{ gettext('Shard Sort') }}
            </button>
            <button
              v-for="option in sortOptions"
              type="button"
              :class="['btn btn-outline-primary', sort === option ? 'active': '']"
              @click="setState('sort', option)"
            >
              {{ gettext('By ' + option) }}
            </button>
          </div>

          <div
            class="btn-group d-block"
            role="group"
          >
            <button
              v-if="!split || !sort || !mix"
              disabled
              class="btn btn-secondary disabled"
            >
              {{ gettext('Select a count, sort, and mix to open a shard') }}
            </button>
            <button
              v-for="(shard, shardIndex) in shardOptions"
              v-else
              type="button"
              :class="['btn btn-success', index === shardIndex ? 'active': '']"
              @click="openShard(shard, shardIndex)"
            >
              {{ gettext('Open') + ' ' + gettext(split) + ' ' + shard }}
            </button>
            <button
              v-if="index !== null"
              class="btn btn-danger"
              @click="closeShard()"
            >
              {{ gettext('Close Shard') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
