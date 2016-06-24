<style>

</style>

<template>

  <div class="vue-draggable adj-draggable btn btn-sm">

    <span data-toggle="tooltip" title="{{ adj.name }} of {{ adj.institution.name }}">
      {{ short_name }}<br>
    </span>

    <span v-if="adj.institution.code" class="small">
      {{ adj.institution.code }}
    </span>
    <span v-else>
      {{ adj.institution.name }}
    </span>

     {{ adj.score }}
  </div>

</template>

<script>
export default {
  props: {
    adj: Object
  },
  computed: {
    short_name: function() {
      var names = this.adj.name.split(" ")
      return names[0] + " " + names[1][0] + ".";
    }
  }
}
</script>
