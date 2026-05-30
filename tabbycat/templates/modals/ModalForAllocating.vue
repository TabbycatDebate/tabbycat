<script setup>
import { computed, ref, toRef } from 'vue'
import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'
import { useModalAction } from '../composables/useModalAction.js'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const props = defineProps({
  introText: String,
  forPanels: {
    type: Boolean,
    default: false,
  },
  forVenues: {
    type: Boolean,
    default: false,
  },
  contextOfAction: String,
})

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()

const modal = ref(null)
const { loading, performWSAction } = useModalAction({
  modalRef: modal,
  contextOfAction: toRef(props, 'contextOfAction'),
})

const extra = computed(() => store.extra)
const settings = ref(JSON.parse(JSON.stringify(extra.value?.allocationSettings ?? {})))

const smartAllocateWithPreformed = () => {
  settings.value.usePreformedPanels = true
  settings.value.allocationMethod = 'hungarian'
  performWSAction(settings.value)
}

const directAllocateWithPreformed = () => {
  settings.value.usePreformedPanels = true
  settings.value.allocationMethod = 'direct'
  performWSAction(settings.value)
}

const allocateIndividualAdjs = () => {
  settings.value.usePreformedPanels = false
  performWSAction(settings.value)
}

const id = 'confirmAllocateModal'
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
      <div class="modal-content">
        <div class="modal-body text-center p-4 bg-bg">
          <p class="font-italic small">
            {{ introText }}
          </p>

          <div
            v-if="!forPanels"
            class="card"
          >
            <div class="card-body p-3">
              <h5 class="card-title mb-0">
                {{ gettext(`Auto-Allocate Preformed Panels`) }}
              </h5>
            </div>
            <div
              v-if="extra.hasPreformedPanels"
              class="list-group list-group-item-flush"
            >
              <div class="list-group-item p-3">
                <button
                  type="submit"
                  :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                  @click="smartAllocateWithPreformed"
                >
                  {{ loading ? gettext('Loading...') : gettext('Smart Allocate') }}
                </button>
                <p class="font-italic small mt-1 mb-1">
                  {{ gettext(`Allocates preformed panels to debates of similar priority level, while avoiding conflicts.`) }}
                </p>
              </div>
              <div class="list-group-item p-3">
                <button
                  type="submit"
                  :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                  @click="directAllocateWithPreformed"
                >
                  {{ loading ? gettext('Loading...') : gettext('Direct Allocate') }}
                </button>
                <p class="font-italic small mt-1 mb-1">
                  {{ gettext(`Allocates panels in exact order going from top to bottom (ignoring debate priority and conflicts.)`) }}
                </p>
              </div>
            </div>
            <div
              v-if="!forPanels && !extra.hasPreformedPanels"
              class="list-group-item p-3"
            >
              <p class="font-italic mb-0">
                {{ gettext(`No preformed panels exist for this round. You can create some by going to Setup, and then Preformed Panels.`) }}
              </p>
            </div>
          </div>

          <div class="card mt-3">
            <div class="card-body p-3">
              <h5 class="card-title mb-0">
                {{ gettext(`Auto-Allocate Individual Adjudicators`) }}
              </h5>
            </div>

            <div
              v-if="!forPanels"
              class="list-group list-group-item py-0"
            >
              <div
                v-if="settings.draw_rules__adj_min_voting_score > extra.adjMaxScore"
                class="alert alert-warning"
              >
                The score required to be allocated as voting panellist ({{ settings.draw_rules__adj_min_voting_score }}) is
                higher than the maximum adjudicator score ({{ extra.adjMaxScore }}).
              </div>
              <div
                v-if="settings.draw_rules__adj_min_voting_score < extra.adjMinScore"
                class="alert alert-warning"
              >
                The score required to be allocated as voting panellist ({{ settings.draw_rules__adj_min_voting_score }}) is
                lower than the minimum  adjudicator score ({{ extra.adjMinScore }}).
              </div>
              <div class="text-left py-3">
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input
                      v-model.number="settings.draw_rules__adj_min_voting_score"
                      type="number"
                      class="form-control"
                    >
                  </div>
                  <label class="col-sm-9 col-form-label">
                    {{ gettext('Minimum feedback score required to be a chair or panellist') }}
                  </label>
                </div>
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input
                      v-model="settings.draw_rules__no_panellist_position"
                      type="checkbox"
                      class="form-control"
                    >
                  </div>
                  <label class="col-sm-9 col-form-label">{{ gettext('Do not allocate panellists') }}</label>
                </div>
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input
                      v-model="settings.draw_rules__no_trainee_position"
                      type="checkbox"
                      class="form-control"
                    >
                  </div>
                  <label class="col-sm-9 col-form-label">{{ gettext('Do not allocate trainees') }}</label>
                </div>
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input
                      v-model.number="settings.draw_rules__adj_history_penalty"
                      type="number"
                      class="form-control"
                    >
                  </div>
                  <label class="col-sm-9 col-form-label">
                    {{ gettext(`History penalty — higher numbers will more strongly avoid
                                         matching adjudicators to teams or panellists they have seen
                                         before`) }}
                  </label>
                </div>
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input
                      v-model.number="settings.draw_rules__adj_conflict_penalty"
                      type="number"
                      class="form-control"
                    >
                  </div>
                  <label class="col-sm-9 col-form-label">{{ gettext('Conflict penalty — higher numbers will more strongly avoid recorded conflicts') }}</label>
                </div>
                <div
                  v-if="forPanels"
                  class="form-group row"
                >
                  <div class="col-sm-3">
                    <input
                      v-model.number="settings.draw_rules__preformed_panel_mismatch_penalty"
                      type="number"
                      class="form-control"
                    >
                  </div>
                  <label class="col-sm-9 col-form-label">
                    {{ gettext(`Importance mismatch penalty — higher numbers will more
                                         strongly match panel strengths to assigned importances`) }}
                  </label>
                </div>
              </div>
            </div>

            <div class="list-group-item pt-2 px-3 pb-0">
              <button
                type="submit"
                :class="['btn btn-block btn-success my-2', loading ? 'disabled': '']"
                @click="allocateIndividualAdjs"
              >
                {{ loading ? gettext('Loading...') : gettext('Auto-Allocate Adjudicators') }}
              </button>
              <p class="font-italic small">
                {{ gettext(`The allocator creates stronger panels for debates that were given
                                  higher importances. If importances have not been set it will allocate
                                  stronger panels to debates in higher brackets.`) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
