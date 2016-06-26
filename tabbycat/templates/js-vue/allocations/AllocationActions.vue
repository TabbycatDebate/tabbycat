<template>
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
        <div v-if="!showingGender && !showingLanguage && !showingRegion"class="btn-group btn-group-sm">
          <div disabled class="btn btn-sm btn-primary">Seen Before</div>
          <div disabled class="btn btn-sm btn-warning">Institutional Conflicts</div>
          <div disabled class="btn btn-sm btn-danger">Personal Conflicts</div>
          <div disabled class="btn btn-sm panel-incomplete">No Chair/Odd Panel</div>
        </div>
        <div v-if="showingGender" class="btn-group btn-group-sm">
          <button disabled class="btn male gender-display">Male</button>
          <button disabled class="btn nm gender-display">Non-Male</button>
          <button disabled class="btn unknown gender-display">Unknown</button>
        </div>
        <div v-if="showingRegion" class="btn-group btn-group-sm">
          <button disabled v-for="region in regions"
            class="btn btn-default region-display region-{{ region.seq }}">
            {{ region.name }}
          </button>
        </div>
        <div v-if="showingLanguage" class="btn-group btn-group-sm">
          <button disabled class="btn break-display break-1">ESL</button>
          <button disabled class="btn break-display break-2">EFL</button>
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
        <button class="btn btn-default nav-link hoverable" v-on:click="showLanguage" v-bind:class="showingLanguage ? 'active' : ''">
          <span class="glyphicon" v-bind:class="showingLanguage ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
          Language
        </button>
      </div>
    </div>

  </nav>
</template>

<script>
export default {
  props: {
    regions: Array,
    showingVenue: { default: false },
    showingRegion: { default: false },
    showingGender: { default: false },
    showingLanguage: { default: false }
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
      this.showingLanguage = false;
      $(".diversity-highlightable").removeClass("gender-display language-display");
    },
    showGender: function() {
      this.showingGender = !this.showingGender;
      $(".diversity-highlightable").toggleClass("gender-display");
      this.showingRegion = false;
      this.showingLanguage = false;
      $(".diversity-highlightable").removeClass("region-display language-display");
    },
    showLanguage: function() {
      this.showingLanguage = !this.showingLanguage;
      this.showingGender = false;
      this.showingRegion = false;
      $(".diversity-highlightable").removeClass("region-display gender-display");
    }
  }
}
</script>
