<template>

  <div class="modal fade" :id="id" tabindex="-1" role="dialog" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4 bg-bg">

          <p class="font-italic small" v-text="introText"></p>

          <div class="card" v-if="!forPanels">
            <div class="card-body p-3">
              <h5 class="card-title mb-0" v-text="gettext(`Auto-Allocate Preformed Panels`)"></h5>
            </div>
            <div class="list-group list-group-item-flush" v-if="extra.hasPreformedPanels">
              <div class="list-group-item p-3">
                <button type="submit" @click="smartAllocateWithPreformed"
                      :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                      v-text="loading ? gettext('Loading...') : gettext('Smart Allocate')"></button>
                <p class="font-italic small mt-1 mb-1" v-text="gettext(`Allocates preformed panels to debates of similar priority level, while avoiding conflicts.`)"></p>
              </div>
              <div class="list-group-item p-3">
                <button type="submit" @click="directAllocateWithPreformed"
                      :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                      v-text="loading ? gettext('Loading...') : gettext('Direct Allocate')"></button>
                <p class="font-italic small mt-1 mb-1" v-text="gettext(`Allocates panels in exact order going from top to bottom (ignoring debate priority and conflicts.)`)"></p>
              </div>
            </div>
            <div class="list-group-item p-3" v-if="!forPanels && !extra.hasPreformedPanels">
              <p class="font-italic mb-0" v-text="gettext(`No preformed panels exist for this round. You can create some by going to Setup, and then Preformed Panels.`)"></p>
            </div>
          </div>

          <div class="card mt-3">

            <div class="card-body p-3">
              <h5 class="card-title mb-0" v-text="gettext(`Auto-Allocate Individual Adjudicators`)"></h5>
            </div>

            <div v-if="!forPanels" class="list-group list-group-item py-0">

              <div v-if="settings.draw_rules__adj_min_voting_score > extra.adjMaxScore" class="alert alert-warning">
                The score required to be allocated as voting panellist ({{ settings.draw_rules__adj_min_voting_score }}) is
                higher than the maximum adjudicator score ({{ extra.adjMaxScore }}).
              </div>
              <div v-if="settings.draw_rules__adj_min_voting_score < extra.adjMinScore" class="alert alert-warning">
                The score required to be allocated as voting panellist ({{ settings.draw_rules__adj_min_voting_score }}) is
                lower than the minimum  adjudicator score ({{ extra.adjMinScore }}).
              </div>
              <div class="text-left py-3">
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input v-model.number="settings.draw_rules__adj_min_voting_score" type="number" class="form-control">
                  </div>
                  <label class="col-sm-9 col-form-label"
                         v-text="gettext('Minimum feedback score required to be a chair or panellist')"></label>
                </div>
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input v-model=settings.draw_rules__no_panellist_position type="checkbox" class="form-control">
                  </div>
                  <label class="col-sm-9 col-form-label" v-text="gettext('Do not allocate panellists')"></label>
                </div>
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input v-model=settings.draw_rules__no_trainee_position type="checkbox" class="form-control">
                  </div>
                  <label class="col-sm-9 col-form-label" v-text="gettext('Do not allocate trainees')"></label>
                </div>
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input v-model.number=settings.draw_rules__adj_history_penalty type="number" class="form-control">
                  </div>
                  <label class="col-sm-9 col-form-label"
                         v-text="gettext(`History penalty — higher numbers will more strongly avoid
                                          matching adjudicators to teams or panellists they have seen
                                          before`)">
                  </label>
                </div>
                <div class="form-group row">
                  <div class="col-sm-3">
                    <input v-model.number=settings.draw_rules__adj_conflict_penalty type="number" class="form-control">
                  </div>
                  <label class="col-sm-9 col-form-label" v-text="gettext('Conflict penalty — higher numbers will more strongly avoid recorded conflicts')"></label>
                </div>
                <div class="form-group row" v-if="forPanels">
                  <div class="col-sm-3">
                    <input v-model.number=settings.draw_rules__preformed_panel_mismatch_penalty type="number" class="form-control">
                  </div>
                  <label class="col-sm-9 col-form-label"
                         v-text="gettext(`Importance mismatch penalty — higher numbers will more
                                          strongly match panel strengths to assigned importances`)">
                  </label>
                </div>
              </div>
            </div>

            <div class="list-group-item pt-2 px-3 pb-0">

              <button type="submit" @click="allocateIndividualAdjs"
                      :class="['btn btn-block btn-success my-2', loading ? 'disabled': '']"
                      v-text="loading ? gettext('Loading...') : gettext('Auto-Allocate Adjudicators')"></button>
              <p class="font-italic small" v-text="gettext(`The allocator creates stronger panels for debates that were given
                                  higher importances. If importances have not been set it will allocate
                                  stronger panels to debates in higher brackets.`)"></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
import { mapState } from 'vuex'

import ModalActionMixin from './ModalActionMixin.vue'

export default {
  mixins: [ModalActionMixin],
  props: {
    introText: String,
    forPanels: {
      type: Boolean,
      default: false,
    },
    forVenues: {
      type: Boolean,
      default: false,
    },
  },
  data: function () {
    return {
      id: 'confirmAllocateModal',
      settings: null,
    }
  },
  created: function () {
    // Clone initial settings to internal state
    this.settings = JSON.parse(JSON.stringify(this.extra.allocationSettings))
  },
  methods: {
    smartAllocateWithPreformed: function () {
      this.settings.usePreformedPanels = true
      this.settings.allocationMethod = 'hungarian'
      this.performWSAction(this.settings)
    },
    directAllocateWithPreformed: function () {
      this.settings.usePreformedPanels = true
      this.settings.allocationMethod = 'direct'
      this.performWSAction(this.settings)
    },
    allocateIndividualAdjs: function () {
      this.settings.usePreformedPanels = false
      this.performWSAction(this.settings)
    },
  },
  computed: mapState(['extra']),
}
</script>
