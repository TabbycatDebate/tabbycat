<template>

  <div class="modal fade" :id="id" tabindex="-1" role="dialog" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4">

          <p class="lead" v-text="introText"></p>

          <div v-if="!forPanels && extra.hasPreformedPanels && !notUsingPreformed">
            <p v-text="gettext(`You can automatically allocate adjudicators to debates by either
                                assigning preformed panels or by using the standard
                                auto-allocator method that places individual adjudicators.`)"></p>
            <button type="submit" @click="allocateWithPreformed"
                    :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                    v-text="loading ? gettext('Loading...') : gettext('Allocate Preformed Panels')"></button>
            <button type="submit" @click="notUsingPreformed = true" class="btn btn-block btn-success mt-4"
                    v-text="gettext('Allocate Individual Adjudicators')"></button>
          </div>

          <div v-if="notUsingPreformed || forPanels || !extra.hasPreformedPanels">

            <p v-text="gettext(`The allocator creates stronger panels for debates that were given
                                higher importances. If importances have not been set it will allocate
                                stronger panels to debates in a higher bracket.`)"></p>

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
                       v-text="gettext('Minimum feedback score required to be allocated as chair or panellist')"></label>
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

            <button type="submit" @click="allocateWithInfill"
                    :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                    v-text="loading ? gettext('Loading...') : gettext('Auto-Allocate Adjudicators')"></button>

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
      notUsingPreformed: false,
    }
  },
  created: function () {
    // Clone initial settings to internal state
    this.settings = JSON.parse(JSON.stringify(this.extra.allocationSettings))
  },
  methods: {
    allocateWithPreformed: function () {
      this.settings.usePreformedPanels = true
      this.performWSAction(this.settings)
    },
    allocateWithInfill: function () {
      this.settings.usePreformedPanels = false
      this.performWSAction(this.settings)
    },
  },
  computed: mapState(['extra']),
}
</script>
