<template>
  <div class="container-fluid allocation-actions">
    <nav class="navbar navbar-default navbar-fixed-top">
      <div class="navbar-form flex-horizontal flex-justify">

        <div class="btn-toolbar">
          <div class="btn-group btn-group-sm">
            <a href="TODO" class="btn btn-default btn-sm" data-toggle="tooltip"
               data-placement="bottom" title="Return to Draw">
              <span class="glyphicon glyphicon-chevron-left"></span>Back
            </a>
            <button class="btn btn-default btn-sm" data-toggle="tooltip" data-placement="bottom"
                    title="Changes allocation are saved whenever an adjudicator's position is changed. Do not edit/change allocations across multiple browsers/computers!">
              <span id="saveTime">No changes</span>
            </button>
            <a class="btn btn-success btn-sm" @click="showAutoAllocationModal">
              Auto Allocate
            </a>
          </div>
        </div>

        <div class="btn-toolbar">
          <div v-if="!highlightRegion && !highlightGender && !highlightCategory" class="btn-group btn-group-sm">
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
          <div v-if="highlightGender" class="btn-group btn-group-sm">
            <button disabled class="btn gender-display gender-male">Male</button>
            <button disabled class="btn gender-display gender-f">Female</button>
            <button disabled class="btn gender-display gender-o">Other</button>
            <button disabled class="btn btn-default">Unknown</button>
          </div>
          <div v-if="highlightRegion" class="btn-group btn-group-sm">
            <button v-for="region in roundInfo.regions" disabled
                    :class="['btn btn-default region-display', 'region-' + region.class]">
              {{ region.name }}
            </button>
          </div>
          <div v-if="highlightCategory" class="btn-group btn-group-sm">
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
            <button @click="toggleHighlight('highlightRegion')"
                    :class="['btn btn-default nav-link hoverable', highlightRegion ? 'active' : '']">
              <span :class="['glyphicon', highlightRegion ? 'glyphicon-eye-close' : 'glyphicon-eye-open']"></span>
              Region
            </button>
            <button @click="toggleHighlight('highlightGender')"
                    :class="['btn btn-default nav-link hoverable', highlightGender ? 'active' : '']">
              <span :class="['glyphicon', highlightGender ? 'glyphicon-eye-close' : 'glyphicon-eye-open']"></span>
              Gender
            </button>
            <button @click="toggleHighlight('highlightCategory')"
                    :class="['btn btn-default nav-link hoverable', highlightCategory ? 'active' : '']">
              <span :class="['glyphicon', highlightCategory ? 'glyphicon-eye-close' : 'glyphicon-eye-open']"></span>
              Category
            </button>
          </div>
        </div>

      </div>
    </nav>

    <allocation-modal :round-info="roundInfo"></allocation-modal>

  </div>
</template>

<script>
import AllocationModal from '../infoovers/AllocationModal.vue'

export default {
  props: { roundInfo: Object },
  components: { AllocationModal },
  data: function() {
    // Internal state storing the status of which modal is being toggled
    return { highlightRegion: false, highlightGender: false, highlightCategory: false }
  },
  methods: {
    showAutoAllocationModal: function() {
      $('#confirmAutoAlert').modal('show');
    },
    toggleHighlight: function(type) {
      // Turn off all highlights; toggle the one just clicked
      this.highlightRegion = type === 'highlightRegion' ? !this[type]: false
      this.highlightGender = type === 'highlightGender' ? !this[type]: false
      this.highlightCategory = type === 'highlightCategory' ? !this[type]: false
      this.$eventHub.$emit('set-highlights', this[type], type)
    }
  }
}

</script>