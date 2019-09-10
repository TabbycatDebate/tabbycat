<template>

  <div class="modal fade" :id="id" tabindex="-1" role="dialog" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-body text-center p-4">

          <p class="lead" v-text="gettext(`Auto-Allocate Venues to Debates`)"></p>
          <p v-text="gettext(`The allocator assigns venues to debates while trying to match
                              all of the venue constraints that have been specified.`)"></p>

          <div class="text-left py-3">
            <div class="form-group row">
              <div class="col-sm-3">
                <select v-model="settings.draw_rules__venue_allocation_method" class="form-control">
                  <option v-text="gettext('Please select')" disabled value=""></option>
                  <option v-text="gettext('Naïve venue assignment')" value="naive"></option>
                  <option v-text="gettext('Hungarian method')" value="hungarian"></option>
                  <option v-text="gettext('Rotation Hungarian')" value="rotate"></option>
                  <option v-text="gettext('Stationary Hungarian')" value="stationary"></option>
                </select>
              </div>
              <label class="col-sm-9 col-form-label" v-text="gettext('The allocation method to use')"></label>
            </div>
            <div v-if="settings.draw_rules__venue_allocation_method != 'naive'">
              <div class="form-group row" v-if="settings.draw_rules__venue_allocation_method != 'hungarian'">
                <div class="col-sm-3">
                  <input v-model.number=settings.draw_rules__venue_history_cost type="number" class="form-control">
                </div>
                <label class="col-sm-9 col-form-label" v-if="settings.draw_rules__venue_allocation_method == 'rotate'"
                       v-text="gettext('History penalty - applied to venues if a team has been in a venue in the same category')">
                </label>
                <label class="col-sm-9 col-form-label" v-else
                       v-text="gettext('History penalty - applied to venues if a team has not been in a venue in the same category')">
                </label>
              </div>
              <div class="form-group row">
                <div class="col-sm-3">
                  <input v-model.number=settings.draw_rules__venue_constraint_cost type="number" class="form-control">
                </div>
                <label class="col-sm-9 col-form-label"
                       v-text="gettext('Constraint penalty — higher numbers will more strongly enforce recorded constraints')"></label>
              </div>
              <div class="form-group row">
                <div class="col-sm-3">
                  <input v-model.number=settings.draw_rules__venue_score_cost type="number" class="form-control">
                </div>
                <label class="col-sm-9 col-form-label"
                       v-text="gettext('Score penalty - higher numbers will more strongly prefer higher-ranking venues')">
                </label>
              </div>
            </div>
          </div>

          <button type="submit" @click="performWSAction(settings)"
                  :class="['btn btn-block btn-success', loading ? 'disabled': '']"
                  v-text="loading ? gettext('Loading...') : gettext('Auto-Allocate')"></button>

        </div>
      </div>
    </div>
  </div>

</template>

<script>
import { mapState } from 'vuex'

import ModalActionMixin from '../../utils/templates/modals/ModalActionMixin.vue'

export default {
  mixins: [ModalActionMixin],
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
  computed: mapState(['extra']),
}
</script>
