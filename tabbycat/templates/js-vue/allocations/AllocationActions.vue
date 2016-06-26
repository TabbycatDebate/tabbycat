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

    <div class="navbar-form navbar-right btn-group btn-group-sm">
      <button class="btn btn-default nav-link hoverable"
              v-on:click="showVenues"
              v-bind:class="[showingVenue ? active : '']">
        <span class="glyphicon"
              v-bind:class="showingVenue ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
        {{ showingVenue ? 'Hide ' : 'Show ' }}Venues
      </button>
      <button class="btn btn-default nav-link hoverable"
              v-on:click="showRegion"
              v-bind:class="[showingRegion ? active : '']">
        <span class="glyphicon"
              v-bind:class="showingRegion ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
        {{ showingRegion ? 'Hide ' : 'Show ' }}Region
      </button>
      <button class="btn btn-default nav-link hoverable"
              v-on:click="showGender"
              v-bind:class="[showingGender ? active : '']">
        <span class="glyphicon"
              v-bind:class="showingGender ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
        {{ showingGender ? 'Hide ' : 'Show ' }}Gender
      </button>
      <button class="btn btn-default nav-link hoverable"
              v-on:click="showLanguage"
              v-bind:class="[showingLanguage ? active : '']">
        <span class="glyphicon"
              v-bind:class="showingLanguage ? 'glyphicon-eye-close' : 'glyphicon-eye-open'"></span>
        {{ showingLanguage ? 'Hide ' : 'Show ' }}Language
      </button>
    </div>

  </nav>

</template>

<script>
export default {
  props: {
    showingVenue: { default: false },
    showingRegion: { default: false },
    showingGender: { default: false },
    showingLanguage: { default: false },
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
      this.showingGender = false;
      this.showingLanguage = false;
      $(".diversity-highlightable").toggleClass("region-display");
    },
    showGender: function() {
      this.showingGender = !this.showingGender;
      this.showingRegion = false;
      this.showingLanguage = false;
      $(".diversity-highlightable").toggleClass("gender-display");
    },
    showLanguage: function() {
      this.showingLanguage = !this.showingLanguage;
      this.showingGender = false;
      this.showingRegion = false;
      $(".diversity-highlightable").toggleClass("");
    }
  }
}
</script>
