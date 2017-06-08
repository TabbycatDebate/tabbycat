<template>

  <!-- ADD tooltip -->
  <button :class="['btn btn-default', customClasses]" data-toggle="tooltip"
          data-placement="bottom" title="Changes are automatically saved; however do not edit/change allocations across multiple browsers/computers at the same time!">
    <span v-if="!lastSaved">No saved changes</span>
    <span v-if="lastSaved">Saved at {{ hours }}:{{ minutes }}</span>
  </button>

</template>

<script>
export default {
  data: function() { return { lastSaved: false } },
  props: { css: String },
  created: function() {
    this.$eventHub.$on('update-saved-counter', this.updateLastSaved)
  },
  methods: {
    updateLastSaved: function() {
      this.lastSaved = new Date()
    }
  },
  computed: {
    customClasses: function() {
      return this.css
    },
    hours: function() {
      return this.lastSaved.getHours()
    },
    minutes: function() {
      var minutes = String(this.lastSaved.getMinutes())
      if (minutes.length === 1) {
        return '0' + minutes
      } else {
        return minutes
      }
    }
  }
}
</script>
