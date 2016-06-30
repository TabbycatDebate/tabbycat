<template>
  <div class="container-fluid">

    <nav class="navbar navbar-default navbar-fixed-top">

      <div class="navbar-form navbar-left btn-group btn-group-sm">
        <a href="backURL" class="btn btn-default btn-sm">
          <span class="glyphicon glyphicon-chevron-left"></span>Back to Draw
        </a>
        <button class="btn btn-success btn-sm" v-on:click="autoAllocate">
          Auto Allocate
        </button>
      </div>

      <div class="navbar-form pull-right">
        <div class="btn-group btn-group-sm">
          <div v-if="!showingGender && !showingCategory && !showingRegion"class="btn-group btn-group-sm">
            <div disabled class="btn btn-sm histories-display seen-1-ago">Seen Before</div>
            <div disabled class="btn btn-sm conflicts-display institutional-conflict">Institutional Conflicts</div>
            <div disabled class="btn btn-sm conflicts-display personal-conflict">Personal Conflicts</div>
            <div disabled class="btn btn-sm panel-incomplete">No Chair/Odd Panel</div>
          </div>
          <div v-if="showingGender" class="btn-group btn-group-sm">
            <button disabled class="btn gender-display gender-male">Male</button>
            <button disabled class="btn gender-display gender-nm">Non-Male</button>
            <button disabled class="btn gender-display gender-unknown">Unknown</button>
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
              {{ category.name }}
            </button>
          </div>
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
</template>

<script>
export default {
  props: {
    regions: Array,
    categories: Array,
    showingVenue: { default: false },
    showingRegion: { default: false },
    showingGender: { default: false },
    showingCategory: { default: false }
  },
  methods: {
    autoAllocate: function() {
      console.log('auto allocate');
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
