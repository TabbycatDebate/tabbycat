<template>

  <div><!-- Need extra top level element; modal cant be inside a .fixed-top -->

    <nav class="navbar navbar-default fixed-top allocation-actions navbar-light pt-3 pb-3 d-flex justify-content-between">

      <div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups">
        <div class="btn-group btn-group-sm">
          <a :href="roundInfo.backUrl" class="btn btn-outline-primary"
             data-toggle="tooltip" data-placement="bottom" title="Return to Draw">
            <i data-feather="chevron-left"></i>Back
          </a>
          <auto-save-counter></auto-save-counter>
        </div>

        <div class="btn-group btn-group-sm ml-2">
          <a class="btn btn-success text-white"
             @click="showModal('#confirmAutoPrioritiseModal')">
            Auto-Prioritise
          </a>
        </div>

        <div class="btn-group btn-group-sm ml-2">
          <a class="btn btn-success text-white"
             @click="showModal('#confirmAutoAllocationModal')">
            Auto-Allocate
          </a>
        </div>
      </div>

      <div class="btn-group btn-group-sm">
        <template v-if="!highlights.region.state && !highlights.gender.state &&
                        !highlights.category.state && !highlights.ranking.state">
          <button class="visible-lg-block btn btn-outline-secondary disabled">
            <span class="d-xl-inline d-none">Highlights</span> Key
          </button>
          <button class="btn conflictable conflicts-toolbar hover-histories-2-ago" data-toggle="tooltip"
                  title="This adjudicator has judged this team (or judged with this adjudicator) in a previous round">
            Seen
          </button>
          <button class="btn conflictable conflicts-toolbar hover-institution" data-toggle="tooltip"
                  title="This adjudicator is from the same institution as this team or panelist.">
            Institution
          </button>
          <button class="btn conflictable conflicts-toolbar hover-adjudicator" data-toggle="tooltip"
                  title="This adjudicator has a nominated conflict with this team or panelist.">
            Conflict
          </button>
          <button class="btn panel-incomplete" data-toggle="tooltip"
                  title="Either a panel is missing a chair, or has a number of panelists that does not produce a voting majority.">
            Incomplete
          </button>
        </template>
        <template v-if="highlights.gender.state">
          <button class="visible-lg-block btn btn-outline-secondary disabled">
            <span class="d-xl-inline d-none">Gender</span> Key
          </button>
          <button class="btn gender-display gender-male">Male</button>
          <button class="btn gender-display gender-f">Female</button>
          <button class="btn gender-display gender-o">Other</button>
          <button class="btn gender-display gender-">Unknown</button>
        </template>
        <template v-if="highlights.region.state">
          <button class="visible-lg-block btn btn-outline-secondary disabled">
            <span class="d-xl-inline d-none">Region</span> Key
          </button>
          <button v-for="region in roundInfo.regions"
                  :class="['btn btn-primary region-display', 'region-' + region.class]">
            {{ region.name }}
          </button>
        </template>
        <template v-if="highlights.category.state">
          <button class="visible-lg-block btn btn-outline-secondary disabled">
            <span class="d-xl-inline d-none">Break</span> Key
          </button>
          <button v-for="bc in roundInfo.categories"
                  :class="['btn btn-primary category-display', 'category-' + bc.class]">
            {{ bc.name }} Break
          </button>
        </template>
        <template v-if="highlights.ranking.state">
          <button class="visible-lg-block btn btn-outline-secondary disabled">
            <span class="d-xl-inline d-none">Rank</span> Key
          </button>
          <button v-for="threshold in percentiles"
                  :class="['btn ranking-display', 'ranking-' + threshold.percentile]">
            {{ threshold.grade }}</button>
        </template>
      </div>

      <div class="btn-group btn-group-sm">
        <button v-for="highlight in highlights"
                @click="toggleHighlight(highlight, highlight.state)"
                :class="['btn btn-outline-primary hoverable disabled',
                         highlights[label] ? 'btn-primary active' : '']">
          <span :class="highlight.state ? 'd-none' : ''">
            <i data-feather="eye"></i>
          </span>
          <span :class="highlight.state ? '' : 'd-none'">
            <i data-feather="eye-off"></i>
          </span>
          {{ titleCase(highlight.label) }}
        </button>
      </div>

    </nav>

    <auto-allocation-modal :round-info="roundInfo"></auto-allocation-modal>
    <auto-importance-modal :round-info="roundInfo"></auto-importance-modal>

  </div>

</template>

<script>
import AutoImportanceModal from '../allocations/AutoImportanceModal.vue'
import AutoAllocationModal from '../allocations/AutoAllocationModal.vue'
import AutoSaveCounter from '../draganddrops/AutoSaveCounter.vue'
import _ from 'lodash'

export default {
  props: { roundInfo: Object, percentiles: Array },
  components: { AutoAllocationModal, AutoImportanceModal, AutoSaveCounter },
  data: function() {
    // Internal state storing the status of which diversity highlight is being toggled
    return {
      highlights: {
        'category': { 'label': 'break', 'state': false },
        'region': { 'label': 'region', 'state': false },
        'gender': { 'label': 'gender', 'state': false },
        'ranking': { 'label': 'rank', 'state': false },
      }
    }
  },
  methods: {
    showModal: function(modalName) {
      $(modalName).modal('show');
    },
    titleCase: function(title) {
      return title.charAt(0).toUpperCase() + title.substr(1)
    },
    toggleHighlight: function(highlight, oldState) {
      _.forEach(this.highlights, function(value, key) {
        value.state = false
      });
      highlight.state = !oldState
      // Turn off all highlights; toggle the one just clicked
      this.$eventHub.$emit('set-highlights', this.highlights)
    }
  }
}

</script>
