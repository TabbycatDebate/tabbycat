<template>

  <!-- ADD tooltip -->
  <button :class="['btn btn-outline-secondary auto-save', customClasses, animationClass]" data-toggle="tooltip"
          data-placement="bottom" title="Changes are automatically saved; however do not edit/change allocations across multiple browsers/computers at the same time!">
    <span :class="[animationClass]">{{ savedAgoDisplay }}</span>
  </button>

</template>

<script>
export default {
  data: function() { return { lastSaved: false, animationClass: '' } },
  props: { css: String },
  created: function() {
    this.$eventHub.$on('update-saved-counter', this.updateLastSaved)
  },
  methods: {
    updateLastSaved: function() {
      this.lastSaved = new Date()
      this.animationClass = "save-flash"
      setTimeout(function () { this.animationClass = "" }.bind(this), 5000)
      setInterval(function(){
        // Slightly increment to trigger savedAgoDisplay updates
        this.lastSaved = new Date(this.lastSaved.getTime() + 0.001)
      }.bind(this), 1000);
    }
  },
  computed: {
    savedAgoDisplay: function() {
      if (!this.lastSaved) { return "No changes" }
      var savedAgo = Math.abs(new Date() - this.lastSaved) / 1000
      if (savedAgo > 59) {
        return "Saved at " + this.hours + ":" + this.minutes
      } else {
        return "Saved " + parseInt(savedAgo) + "s ago"
      }
    },
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
  },
}
</script>
