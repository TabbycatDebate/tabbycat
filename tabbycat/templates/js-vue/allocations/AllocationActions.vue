<template>
  <div class="container-fluid">

    <nav class="navbar navbar-default navbar-fixed-top">

      <div class="navbar-form navbar-left btn-group btn-group-sm">
        <a href="{{ roundInfo.backToDrawURL }}" class="btn btn-default btn-sm">
          <span class="glyphicon glyphicon-chevron-left"></span>
          Back to {{ roundInfo.roundName }} Draw
        </a>
        <a class="btn btn-success btn-sm" v-on:click="confirmAutoAllocation">
          Auto Allocate
        </a>
      </div>

      <div class="navbar-form pull-right">
        <div v-if="!showingGender && !showingCategory && !showingRegion" class="btn-group btn-group-sm">
          <button disabled class="btn conflictable conflicts-toolbar conflict-hover-2-ago">
            Seen Before
          </button>
          <button disabled class="btn conflictable conflicts-toolbar conflict-hover-institutional-conflict">
            Institutional Conflict
          </button>
          <button disabled class="btn conflictable conflicts-toolbar conflict-hover-personal-conflict">
            Personal Conflict
          </button>
          <button disabled class="btn panel-incomplete">
            Unviable Panel
          </button>
        </div>
        <div v-if="showingGender" class="btn-group btn-group-sm">
          <button disabled class="btn gender-display gender-male">Male</button>
          <button disabled class="btn gender-display gender-f">Female</button>
          <button disabled class="btn gender-display gender-o">Other</button>
          <button disabled class="btn btn-default">Unknown</button>
        </div>
        <div v-if="showingRegion" class="btn-group btn-group-sm">
          <button disabled v-for="region in regions"
            class="btn btn-default region-display region-{{ region.seq }}">
            {{ region.name }}
          </button>
        </div>
        <div v-if="showingCategory" class="btn-group btn-group-sm">
          <button disabled v-for="category in categories"
            class="btn btn-default category-display category-{{ category.seq }}">
            {{ category.name }} Break
          </button>
          <button disabled class="btn btn-default">
            No Category Assigned
          </button>
        </div>
        <div class="btn-group btn-group-sm">
          <button class="btn btn-default nav-link hoverable" v-on:click="showRegion" v-bind:class="showingRegion ? 'active' : ''">
            <span class="glyphicon" v-bind:class="showingRegion ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
            Region
          </button>
          <button class="btn btn-default nav-link hoverable" v-on:click="showGender" v-bind:class="showingGender ? 'active' : ''">
            <span class="glyphicon" v-bind:class="showingGender ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
            Gender
          </button>
          <button class="btn btn-default nav-link hoverable" v-on:click="showCategory" v-bind:class="showingCategory ? 'active' : ''">
            <span class="glyphicon" v-bind:class="showingCategory ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
            Category
          </button>
        </div>
      </div>

    </nav>
  </div>

  <div class="modal fade" id="confirmAutoAlert" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-body">
          <p class="lead">Using auto-allocate will <strong>remove all existing adjudicator allocations</strong> and
          create new panels for all debates.</p>
          <p class="">The allocator forms stronger panels for debates that have been assigned higher importances.
          If importances have not been set, or are equivalent, it will give stronger panels to
          debates of a higher bracket.</p>
          <p class="">Adjudicators must have a feedback score over <strong>{{ roundInfo.scoreForVote }}</strong> to panel.
          You can change this in the <em>Draw Rules</em> section of Configuration if needed.</p>
          <div v-if="roundInfo.scoreForVote > roundInfo.scoreMax" class="alert alert-warning">
            The score required to panel ({{ roundInfo.scoreForVote }}) is higher than the maximum adjudicator score ({{ roundInfo.scoreMax }}).
            You should probably lower the score required to panel in settings.
          </div>
          <div v-if="roundInfo.scoreForVote < roundInfo.scoreMin" class="alert alert-warning">
            The score required to panel ({{ roundInfo.scoreForVote }}) is lower than the minimum adjudicator score ({{ roundInfo.scoreMin }}).
            You should probably raise the score required to panel in settings.
          </div>
          <button type="submit" class="btn btn-block btn-success"
                  v-on:click="createAutoAllocation"
                  data-loading-text="Loading Auto Allocation...">
            Create Automatic Allocation
          </button>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
export default {
  props: {
    regions: Array,
    categories: Array,
    roundInfo: Object,
    showingVenue: { default: false },
    showingRegion: { default: false },
    showingGender: { default: false },
    showingCategory: { default: false }
  },
  methods: {
    confirmAutoAllocation: function() {
      $('#confirmAutoAlert').modal('show');
    },
    resetAutoAllocationModal: function(button) {
      $(button).button('reset');
      $('#confirmAutoAlert').modal('hide');
    },
    createAutoAllocation: function(event) {
      var self = this
      $(event.target).button('loading')
      $.getJSON({
        url: this.roundInfo.createAutoAllocationURL,
        success: function(data, textStatus, jqXHR) {
          self.resetAutoAllocationModal(event.target)
          $.fn.showAlert('success', '<strong>Success:</strong> loaded the auto allocation', 10000)
          self.$dispatch('set-debate-panels', JSON.parse(data))
        },
        error: function(data, textStatus, jqXHR) {
          self.resetAutoAllocationModal(event.target)
          $.fn.showAlert('danger', '<strong>Auto Allocation failed:</strong> ' + data.responseText, 0)
        }
      });
    },
    showRegion: function() {
      this.showingRegion = !this.showingRegion;
      this.showingGender = false;
      this.showingCategory = false;
      this.$dispatch('set_diversity_highlights', this.showingRegion, 'region_show')
    },
    showGender: function() {
      this.showingGender = !this.showingGender;
      this.showingRegion = false;
      this.showingCategory = false;
      this.$dispatch('set_diversity_highlights', this.showingGender, 'gender_show')
    },
    showCategory: function() {
      this.showingCategory = !this.showingCategory;
      this.showingGender = false;
      this.showingRegion = false;
      this.$dispatch('set_diversity_highlights', this.showingCategory, 'category_show')
    }
  }
}
</script>
