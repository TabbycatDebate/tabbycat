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

    <div class="navbar-form pull-right btn-group btn-group-sm">
      <button class="btn btn-default nav-link hoverable" v-on:click="showVenues" v-bind:class="showingVenue ? 'active' : 'notactive'">
        <span class="glyphicon" v-bind:class="showingVenue ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
        {{ showingVenue ? 'Hide ' : 'Show ' }}Venues
      </button>
      <button class="btn btn-default nav-link hoverable" v-on:click="showRegion" v-bind:class="showingRegion ? 'active' : ''">
        <span class="glyphicon" v-bind:class="showingRegion ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
        {{ showingRegion ? 'Hide ' : 'Show ' }}Region
      </button>
      <button class="btn btn-default nav-link hoverable" v-on:click="showGender" v-bind:class="showingGender ? 'active' : ''">
        <span class="glyphicon" v-bind:class="showingGender ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
        {{ showingGender ? 'Hide ' : 'Show ' }}Gender
      </button>
      <button class="btn btn-default nav-link hoverable" v-on:click="showLanguage" v-bind:class="showingLanguage ? 'active' : ''">
        <span class="glyphicon" v-bind:class="showingLanguage ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
        {{ showingLanguage ? 'Hide ' : 'Show ' }}Language
      </button>
    </div>

    <div class="navbar-right navbar-form">
      <div v-if="!showingGender && !showingLanguage && !showingRegion"class="btn-group btn-group-sm">
        <div disabled class="btn btn-sm btn-default btn-primary">Seen Previously</div>
        <div disabled class="btn btn-sm btn-default btn-warning">Institutional Conflict</div>
        <div disabled class="btn btn-sm btn-default btn-danger">Personal Conflict</div>
        <div disabled class="btn btn-sm btn-default panel-incomplete">No Chair or Odd Panel</div>
      </div>
      <div v-if="showingGender" class="btn-group btn-group-sm">
        <button disabled class="btn btn-default male gender-display">Male</button>
        <button disabled class="btn btn-default nm gender-display">Non-Male</button>
        <button disabled class="btn btn-default unknown gender-display">Unknown</button>
      </div>
      <div v-if="showingRegion" class="btn-group btn-group-sm">
        <button disabled class="btn btn-default region-display region-1">Region1</button>
        <button disabled class="btn btn-default region-display region-2">Region2</button>
        <button disabled class="btn btn-default region-display region-3">Region3</button>
        <button disabled class="btn btn-default region-display region-4">Region4</button>
      </div>
      <div v-if="showingLanguage" class="btn-group btn-group-sm">
        <button disabled class="btn btn-default male gender-display">ESL</button>
        <button disabled class="btn btn-default nm gender-display">EFL</button>
      </div>
    </div>

  </nav>
</template>

<script>
export default {
  props: {
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
