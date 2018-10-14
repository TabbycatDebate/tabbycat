<template>

  <button :class="['btn btn-link btn-no-hover border-primary auto-save', animationClass]">
    <span v-if="lastSavedDisplay === ''" v-text="gettext('No changes')"></span>
    <span v-else :class="[animationClass]">{{ lastSavedDisplay }}</span>
  </button>

</template>

<script>
export default {
  props: { css: String },
  data: () => ({
    lastSavedDisplay: '', animationClass: '', currentTimer: null,
  }),
  watch: {
    lastSaved: function (lastSaved) {
      // When the last saved store updates trigger updates to the display text once a second for 60s
      clearInterval(this.currentTimer)
      this.updatedLastSavedDisplay()
      this.animationClass = 'save-flash'
      this.currentTimer = setInterval(() => {
        this.updatedLastSavedDisplay()
      }, 1000)
    },
  },
  methods: {
    updatedLastSavedDisplay: function () {
      const secondsLastSaved = Math.abs(new Date() - this.lastSaved) / 1000
      if (secondsLastSaved > 5) {
        this.animationClass = '' // Remove animation flash
      }
      if (secondsLastSaved > 59) {
        this.lastSavedDisplay = `Saved at ${this.lastSaved.getHours()}:${this.paddedMinutes()}`
      } else {
        this.lastSavedDisplay = `Saved ${parseInt(secondsLastSaved)}s ago`
      }
    },
    paddedMinutes: function () {
      const minutes = String(this.lastSaved.getMinutes())
      if (minutes.length === 1) {
        return `0${minutes}`
      }
      return minutes
    },
  },
  computed: {
    lastSaved: function () {
      return this.$store.state.lastSaved
    },
  },
}
</script>
