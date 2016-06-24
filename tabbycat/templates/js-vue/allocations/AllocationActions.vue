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
      <button class="btn btn-default nav-link hoverable">
        <span class="glyphicon glyphicon glyphicon-eye-open"></span>
        Show Venues
      </button>
      <button class="btn btn-default nav-link hoverable">
        <span class="glyphicon glyphicon glyphicon-eye-open"></span>
        Show Region
      </button>
      <button class="btn btn-default nav-link hoverable">
        <span class="glyphicon glyphicon glyphicon-eye-open"></span>
        Show Gender
      </button>
      <button class="btn btn-default nav-link hoverable">
        <span class="glyphicon glyphicon glyphicon-eye-open"></span>
        Show Language
      </button>
    </div>

  </nav>

</template>

<script>
export default {
  methods: {
    autoAllocate: function() {
      console.log('auto allocate');
    }
  }
}
</script>
