<template>

  <button :class="['btn px-0 border-primary text-primary d-xl-inline d-none vc-auto-save', animationClass]"
          data-toggle="tooltip" data-placement="bottom"
          :title="gettext('The time of the last saved change (changes are automatically saved)')">
    <span v-if="lastSavedDisplay === ''">
      <span v-text="gettext('No ')"></span> <i data-feather="save"></i>
    </span>
    <span v-if="lastSavedDisplay !== ''" :class="[animationClass]">{{ lastSavedDisplay }}</span>
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
        this.lastSavedDisplay = ` at ${this.lastSaved.getHours()}:${this.paddedMinutes()}`
      } else {
        this.lastSavedDisplay = ` ${parseInt(secondsLastSaved)}s ago`
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

<style scoped>
  .vc-auto-save {
    min-width: 70px; /* Ensure no resize on save */
  }
</style>
