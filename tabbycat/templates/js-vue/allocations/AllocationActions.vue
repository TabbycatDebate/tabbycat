<template>
  <div class="container-fluid allocation-actions">
    <nav class="navbar navbar-default navbar-fixed-top">
      <div class="navbar-form flex-horizontal flex-justify">

        <div class="btn-toolbar">
          <div class="btn-group btn-group-sm">
            <a :href="roundInfo.backUrl" class="btn btn-default btn-sm" data-toggle="tooltip"
               data-placement="bottom" title="Return to Draw">
              <span class="glyphicon glyphicon-chevron-left"></span>Back
            </a>
            <auto-save-counter :css="'btn-sm'"></auto-save-counter>
            <a class="btn btn-success btn-sm" @click="showAutoAllocationModal">
              Auto Allocate
            </a>
          </div>
        </div>

        <div class="btn-toolbar">
          <div class="btn-group btn-group-sm">
            <template v-if="!highlights.region && !highlights.gender &&
                            !highlights.category && !highlights.ranking">
              <button class="visible-lg-block btn btn-default">Conflicts Key</button>
              <button class="btn conflictable conflicts-toolbar hover-history-2-ago">
                Seen Before
              </button>
              <button class="btn conflictable conflicts-toolbar hover-institutional">
                Institutional <span class="visible-lg-inline">Clash</span>
              </button>
              <button class="btn conflictable conflicts-toolbar hover-personal">
                Personal <span class="visible-lg-inline">Clash</span>
              </button>
              <button class="btn panel-incomplete">
                Unbalanced
              </button>
            </template>
            <template v-if="highlights.gender">
              <button class="visible-lg-block btn btn-default">Gender Key</button>
              <button class="btn gender-display gender-male">Male</button>
              <button class="btn gender-display gender-f">Female</button>
              <button class="btn gender-display gender-o">Other</button>
              <button class="btn gender-display gender-">Unknown</button>
            </template>
            <template v-if="highlights.region">
              <button class="visible-lg-block btn btn-default">Region Key</button>
              <button v-for="region in roundInfo.regions"
                      :class="['btn btn-default region-display', 'region-' + region.class]">
                {{ region.name }}
              </button>
            </template>
            <template v-if="highlights.category">
              <button class="visible-lg-block btn btn-default">Category Key</button>
              <button v-for="category in roundInfo.categories"
                      :class="['btn btn-default category-display', 'category-' + category.class]">
                {{ category.name }} Break
              </button>
              <button  class="btn btn-default">
                None Assigned
              </button>
            </template>
            <template v-if="highlights.ranking">
              <button class="visible-lg-block btn btn-default">Ranking Key</button>
              <button v-for="threshold in percentiles"
                      :class="['btn ranking-display', 'ranking-' + threshold.percentile]">
                {{ threshold.grade }}</button>
            </template>
          </div>
        </div>
        <div class="btn-toolbar">
          <div class="btn-group btn-group-sm">
            <button v-for="label in highlightLabels" @click="toggleHighlight(label)"
                    :class="['btn btn-default nav-link hoverable', highlights[label] ? 'active' : '']">
              <span :class="['glyphicon', highlights[label] ? 'glyphicon-eye-close' : 'glyphicon-eye-open']"></span>
              {{ titleCase(label) }}
            </button>
          </div>
        </div>

      </div>
    </nav>

    <allocation-modal :round-info="roundInfo"></allocation-modal>

  </div>
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
