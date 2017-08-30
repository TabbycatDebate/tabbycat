<template>

  <nav class="navbar navbar-default fixed-top allocation-actions pt-3 bg-light pb-3 d-flex justify-content-between">

    <div class="btn-group">
      <div class="btn-group btn-group-sm">
        <a :href="roundInfo.backUrl" class="btn btn-outline-primary btn-sm" data-toggle="tooltip"
           data-placement="bottom" title="Return to Draw">
          <i data-feather="chevron-left"></i>Back
        </a>
        <auto-save-counter :css="'btn-sm'"></auto-save-counter>
        <a class="btn btn-success text-white btn-sm" @click="showAutoAllocationModal">
          Auto Allocate
        </a>
      </div>
    </div>

    <div class="btn-group">
      <div class="btn-group btn-group-sm">
        <template v-if="!highlights.region && !highlights.gender &&
                        !highlights.category && !highlights.ranking">
          <button class="visible-lg-block btn btn-outline-secondary">Conflicts Key</button>
          <button class="btn conflictable conflicts-toolbar hover-histories-2-ago disabled">
            Seen Before
          </button>
          <button class="btn conflictable conflicts-toolbar hover-institution disabled">
            Institutional <span class="d-lg-inline d-none">Clash</span>
          </button>
          <button class="btn conflictable conflicts-toolbar hover-adjudicator disabled">
            Personal <span class="d-lg-inline d-none">Clash</span>
          </button>
          <button class="btn panel-incomplete disabled">
            Unbalanced <span class="d-lg-inline d-none">Panel</span>
          </button>
        </template>
        <template v-if="highlights.gender">
          <button class="visible-lg-block btn btn-outline-secondary disabled">Gender Key</button>
          <button class="btn gender-display gender-male">Male</button>
          <button class="btn gender-display gender-f">Female</button>
          <button class="btn gender-display gender-o">Other</button>
          <button class="btn gender-display gender-">Unknown</button>
        </template>
        <template v-if="highlights.region">
          <button class="visible-lg-block btn btn-outline-secondary">Region Key</button>
          <button v-for="region in roundInfo.regions"
                  :class="['btn btn-primary region-display', 'region-' + region.class]">
            {{ region.name }}
          </button>
        </template>
        <template v-if="highlights.category">
          <button class="visible-lg-block btn btn-outline-secondary">Category Key</button>
          <button v-for="category in roundInfo.categories"
                  :class="['btn btn-primary category-display', 'category-' + category.class]">
            {{ category.name }} Break
          </button>
          <button  class="btn btn-primary">
            None Assigned
          </button>
        </template>
        <template v-if="highlights.ranking">
          <button class="visible-lg-block btn btn-outline-secondary">Ranking Key</button>
          <button v-for="threshold in percentiles"
                  :class="['btn ranking-display', 'ranking-' + threshold.percentile]">
            {{ threshold.grade }}</button>
        </template>
      </div>
    </div>

    <div class="btn-group">
      <div class="btn-group btn-group-sm">
        <button v-for="label in highlightLabels" @click="toggleHighlight(label)"
                :class="['btn btn-primary hoverable disabled', highlights[label] ? 'active' : '']">
          <span :class="highlights[label] ? 'd-none' : ''">
            <i data-feather="eye"></i>
          </span>
          <span :class="highlights[label] ? '' : 'd-none'">
            <i data-feather="eye-off"></i>
          </span>
          {{ titleCase(label) }}
        </button>
      </div>
    </div>

    <allocation-modal :round-info="roundInfo"></allocation-modal>

  </nav>

</template>

<script>
import AllocationModal from '../allocations/AllocationModal.vue'
import AutoSaveCounter from '../draganddrops/AutoSaveCounter.vue'

export default {
  props: { roundInfo: Object, percentiles: Array },
  components: { AllocationModal, AutoSaveCounter },
  data: function() {
    // Internal state storing the status of which diversity highlight is being toggled
    return {
      highlights: { region: false, gender: false, category: false, ranking: false },
      highlightLabels: { region: 'region', gender: 'gender', category: 'category', ranking: 'ranking' }
    }
  },
  methods: {
    showAutoAllocationModal: function() {
      $('#confirmAutoAlert').modal('show');
    },
    titleCase: function(title) {
      return title.charAt(0).toUpperCase() + title.substr(1)
    },
    toggleHighlight: function(label) {
      // Turn off all highlights; toggle the one just clicked
      this.highlights.region = label === 'region' ? !this.highlights[label]: false
      this.highlights.gender = label === 'gender' ? !this.highlights[label]: false
      this.highlights.category = label === 'category' ? !this.highlights[label]: false
      this.highlights.ranking = label === 'ranking' ? !this.highlights[label]: false
      this.$eventHub.$emit('set-highlights', this.highlights)
    }
  }
}

</script>
