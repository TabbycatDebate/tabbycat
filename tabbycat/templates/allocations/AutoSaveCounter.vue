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
// Note this has to work across the VueX pages (where save updates are located in the store) and
// across checkbox tables (where save updates are notified over the event hub)

export default {
  props: { css: String },
  data: () => ({
    lastSavedTime: null, lastSavedDisplay: '', animationClass: '', currentTimer: null,
  }),
  created () {
    this.$eventHub.$on('update-saved-counter', this.updateLastSavedTimeFromEvent)
  },
  watch: {
    lastSavedFromStore: function (time) {
      // When the last saved store updates set the local variable to match
      this.lastSavedTime = time
    },
    lastSavedTime: function (time) {
      // When the local time updates, display it
      clearInterval(this.currentTimer)
      this.updatedLastSavedDisplay()
      this.animationClass = 'save-flash'
      this.currentTimer = setInterval(() => {
        this.updatedLastSavedDisplay()
      }, 1000)
    },
  },
  methods: {
    updateLastSavedTimeFromEvent: function (time) {
      this.lastSavedTime = time
    },
    updatedLastSavedDisplay: function () {
      const secondsLastSaved = Math.abs(new Date() - this.lastSavedTime) / 1000
      if (secondsLastSaved > 5) {
        this.animationClass = '' // Remove animation flash
      }
      if (secondsLastSaved > 59) {
        this.lastSavedDisplay = ` at ${this.lastSavedTime.getHours()}:${this.paddedMinutes()}`
      } else {
        this.lastSavedDisplay = ` ${parseInt(secondsLastSaved)}s ago`
      }
    },
    paddedMinutes: function () {
      const minutes = String(this.lastSavedTime.getMinutes())
      if (minutes.length === 1) {
        return `0${minutes}`
      }
      return minutes
    },
  },
  computed: {
    lastSavedFromStore: function () {
      return this.$store.state.lastSaved
    },
  },
}
</script>
