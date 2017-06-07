<template>
  <div class="container-fluid allocation-actions">
    <nav class="navbar navbar-default navbar-fixed-top">
      <div class="navbar-form flex-horizontal flex-justify">

        <div class="btn-toolbar">
          <div class="btn-group btn-group-sm">
            <a :href="backUrl" class="btn btn-default btn-sm" data-toggle="tooltip"
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
          <div v-if="!highlights.region && !highlights.gender && !highlights.category" class="btn-group btn-group-sm">
            <button disabled class="btn conflictable conflicts-toolbar conflict-hover-2-ago">
              Seen Before
            </button>
            <button disabled class="btn conflictable conflicts-toolbar conflict-hover-institutional-conflict">
              Institutional Clash
            </button>
            <button disabled class="btn conflictable conflicts-toolbar conflict-hover-personal-conflict">
              Personal Clash
            </button>
            <button disabled class="btn panel-incomplete">
              Unbalanced
            </button>
          </div>
          <div v-if="highlights.gender" class="btn-group btn-group-sm">
            <button disabled class="btn gender-display gender-male">Male</button>
            <button disabled class="btn gender-display gender-f">Female</button>
            <button disabled class="btn gender-display gender-o">Other</button>
            <button disabled class="btn btn-default">Unknown</button>
          </div>
          <div v-if="highlights.region" class="btn-group btn-group-sm">
            <button v-for="region in roundInfo.regions" disabled
                    :class="['btn btn-default region-display', 'region-' + region.class]">
              {{ region.name }}
            </button>
          </div>
          <div v-if="highlights.category" class="btn-group btn-group-sm">
            <button v-for="category in roundInfo.categories" disabled
                    :class="['btn btn-default category-display', 'category-' + category.class]">
              {{ category.name }} Break
            </button>
            <button disabled class="btn btn-default">
              No Category Assigned
            </button>
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
  props: { roundInfo: Object, backUrl: String },
  components: { AllocationModal, AutoSaveCounter },
  data: function() {
    // Internal state storing the status of which diversity highlight is being toggled
    return { highlights: { region: false, gender: false, category: false },
             highlightLabels: { region: 'region', gender: 'gender', category: 'category' }, }
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
      this.$eventHub.$emit('set-highlights', this.highlights)
    }
  }
}

</script>