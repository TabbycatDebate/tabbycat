<script setup>
import _ from 'lodash'
import { computed, ref } from 'vue'
import AutoSaveCounter from '../../templates/allocations/AutoSaveCounter.vue'
import TablesContainer from './TablesContainer.vue'
import { useAjax } from '../composables/useAjax.js'
import { useCookie } from '../composables/useCookie.js'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const props = defineProps({
  tablesData: Array,
  categories: Array,
  urls: Object,
  navigation: Array,
  roundInfo: Object,
  translations: Object,
  hideAutoSave: Boolean,
})

const { gettext } = useDjangoI18n()
const { getCookie } = useCookie()

const lastSaved = ref(null)
const onSaveSuccess = (time) => {
  lastSaved.value = time
}

const { ajaxSave } = useAjax(onSaveSuccess)

const tablesData = ref(props.tablesData)

const checked = computed(() => {
  const checked = {}
  _.forEach(props.categories, (category) => {
    checked[category.id] = {}
  })
  _.forEach(tablesData.value[0].data, (row) => {
    _.forEach(row, (column) => {
      if (!_.isUndefined(column.type)) {
        const breakData = { type: column.type, checked: column.checked }
        checked[column.type][column.id] = breakData
      }
    })
  })
  return checked
})

const csrftoken = computed(() => getCookie('csrftoken'))

const saveChecks = (type) => {
  const payload = checked.value[type]
  const message = `Checks for ${payload?.id} as ${payload?.checked}`
  ajaxSave(props.urls.save, payload, message, null, null, null, null)
}

const toggleChecked = (cd) => {
  saveChecks(cd.type)
}

const copyFromPrevious = () => {
  _.forEach(tablesData.value[0].data, (row) => {
    row[0].checked = row[0].prev
    row[0].sort = row[0].prev
  })
  saveChecks(0)
}

const setFromCheckIns = (set, unset) => {
  _.forEach(tablesData.value[0].data, (row) => {
    if (set && row[0].checked_in) {
      row[0].checked = true
      row[0].sort = true
    } else if (unset && !row[0].checked_in) {
      row[0].checked = false
      row[0].sort = false
    }
  })
  saveChecks(0)
}

const massSelect = (state, type) => {
  _.forEach(tablesData.value[0].data, (row) => {
    _.forEach(row, (column) => {
      if (column.type === type) {
        column.checked = state
        column.sort = state
      }
    })
  })
  if (!props.hideAutoSave) {
    saveChecks(type)
  }
}

</script>

<template>
  <div>
    <div class="row">
      <div class="col d-flex justify-content-between mb-4">
        <div class="btn-group">
          <a
            v-for="item in navigation"
            :key="item.title"
            :href="item.url"
            class="btn btn-outline-primary"
          >
            <i
              v-if="item.back"
              data-feather="chevron-left"
            />{{ item.title }}
          </a>
        </div>

        <div
          v-for="(bc, index) in categories"
          :key="index"
          class="btn-group"
        >
          <button
            v-if="categories.length > 1"
            class="btn btn-secondary"
          >
            {{ bc.name }}
          </button>
          <button
            class="btn btn-primary"
            type="button"
            @click="massSelect(true, bc.id)"
          >
            <i data-feather="check-circle" /> All
          </button>
          <button
            class="btn btn-primary"
            type="button"
            @click="massSelect(false, bc.id)"
          >
            <i data-feather="x-circle" /> None
          </button>
        </div>

        <template v-if="roundInfo">
          <!-- Extensions just for availabilities -->
          <form
            v-if="roundInfo.break === 'True' && roundInfo.model === 'participants.Adjudicator'"
            :action="urls.breakingAdjs"
            method="post"
          >
            <button
              class="btn btn-primary"
              type="submit"
            >
              <input
                type="hidden"
                name="csrfmiddlewaretoken"
                :value="csrftoken"
              >
              <i data-feather="star" /> {{ gettext("Set Breaking") }}
            </button>
          </form>
          <div class="btn-group">
            <button
              v-if="roundInfo.prev"
              class="btn btn-primary"
              type="button"
              data-toggle="tooltip"
              :title="gettext(`Set all the availabilities to exactly match
                                     what they were in the previous round.`)"
              @click="copyFromPrevious"
            >
              <i data-feather="repeat" /> {{ gettext("Match") }} {{ roundInfo.prev }}
            </button>
            <button
              class="btn btn-primary"
              type="button"
              data-toggle="tooltip"
              :title="gettext('Set all availabilities to exactly match check-ins.')"
              @click="setFromCheckIns(true, true)"
            >
              <i data-feather="repeat" /> {{ gettext("Match Check-Ins") }}
            </button>
            <button
              class="btn btn-primary"
              type="button"
              data-toggle="tooltip"
              :title="gettext(`Set people who are checked in as available
                                     (leave people not checked in unchanged)`)"
              @click="setFromCheckIns(true, false)"
            >
              <i data-feather="corner-up-right" /> {{ gettext(" Set Checked-In as Available") }}
            </button>
            <button
              class="btn btn-primary"
              type="button"
              data-toggle="tooltip"
              :title="gettext(`Set people who are not checked in as unavailable
                                     (leave people who are checked in unchanged)`)"
              @click="setFromCheckIns(false, true)"
            >
              <i data-feather="corner-down-left" /> {{ gettext(" Set Not Checked-In as Unavailable") }}
            </button>
          </div>
        </template>

        <auto-save-counter
          v-if="!hideAutoSave"
          :css="'btn-md'"
          :last-saved="lastSaved"
        />
      </div>
    </div>

    <div class="row">
      <div class="col">
        <tables-container
          :tables-data="tablesData"
          @toggle-checked="toggleChecked"
        />
      </div>
    </div>
  </div>
</template>
