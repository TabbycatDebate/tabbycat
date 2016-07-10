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
          <button class="btn btn-default conflictable conflict-hover-2-ago">
            Seen Before
          </button>
          <button class="btn btn-default conflictable conflict-hover-institutional-conflict">
            Institutional Conflicts
          </button>
          <button class="btn btn-default conflictable conflict-hover-personal-conflict">
            Personal Conflicts
          </button>
          <button class="btn btn-default panel-incomplete">
            No Chair/Odd Panel
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
        </div>
        <div class="btn-group btn-group-sm">
          <button class="btn btn-default nav-link hoverable" v-on:click="showVenues" v-bind:class="showingVenue ? 'active' : 'notactive'">
            <span class="glyphicon" v-bind:class="showingVenue ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
            Venues
          </button>
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
          <p class="lead">It will form stronger panels for debates that have been assigned higher importances.
          If importances have not been set, or are equivalent, it will give instead give stronger panels to
          debates of a higher bracket.</p>
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
    createAutoAllocation: function(event) {
      console.log('Creating auto allocation');
      $(event.target).button('loading')
      var xhr = new XMLHttpRequest()
      var self = this
      xhr.open('GET', this.roundInfo.createAutoAllocationURL)
      xhr.onload = function () {
        console.log('got allocation back');
        console.log(JSON.parse(xhr.responseText));
        $('#confirmAutoAlert').modal('hide');
        $(event.target).button('reset')
        // TODO: dispatch and event up the chain to replace debates
        // TODO: how to handle errors and the like (test with unreleased/released)
      }
      xhr.send()
    },
    showVenues: function() {
      this.showingVenue = !this.showingVenue;
    },
    showRegion: function() {
      this.showingRegion = !this.showingRegion;
      $(".diversity-highlightable").toggleClass("region-display");
      this.showingGender = false;
      this.showingCategory = false;
      $(".diversity-highlightable").removeClass("gender-display category-display");
    },
    showGender: function() {
      this.showingGender = !this.showingGender;
      $(".diversity-highlightable").toggleClass("gender-display");
      this.showingRegion = false;
      this.showingCategory = false;
      $(".diversity-highlightable").removeClass("region-display category-display");
    },
    showCategory: function() {
      $(".diversity-highlightable").toggleClass("category-display");
      this.showingCategory = !this.showingCategory;
      this.showingGender = false;
      this.showingRegion = false;
      $(".diversity-highlightable").removeClass("region-display gender-display");
    }
  }
}
</script>
