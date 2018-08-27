<template>
  <div class="card-deck">
    <div class="card mb-3">
      <div class="card-body text-center pb-1 row">

        <div class="col">
          <div class="progress">
            <div class="progress-bar bg-primary" role="progressbar"
                 :style="{ width: checksWidths.checked }"
                 data-toggle="tooltip" title="gettext('Checked-In')">
              <i data-feather="x"></i>&nbsp;&nbsp;{{ checks.checked }}
            </div>
            <div class="progress-bar bg-secondary" role="progressbar"
                 :style="{ width: checksWidths.missing }"
                 data-toggle="tooltip" title="gettext('Not Checked-In')">
              <i data-feather="circle"></i>&nbsp;&nbsp;{{ checks.missing }}
            </div>
          </div>
          <h6 class="pt-3 text-center text-secondary" v-text="gettext('Ballot Check-Ins')"></h6>
        </div>

        <div class="col">
          <div class="progress">
            <div class="progress-bar bg-danger" role="progressbar"
                :style="{ width: statusWidths.none }"
                 data-toggle="tooltip" title="gettext('Unknown')">
              <i data-feather="x"></i>&nbsp;&nbsp;{{ statuses.none }}
            </div>
            <div class="progress-bar bg-info" role="progressbar"
                 :style="{ width: statusWidths.draft }"
                 data-toggle="tooltip" title="gettext('Unconfirmed')">
              <i data-feather="circle"></i>&nbsp;&nbsp;{{ statuses.draft }}
            </div>
            <div class="progress-bar bg-success" role="progressbar"
                 :style="{ width: statusWidths.confirmed }"
                 data-toggle="tooltip" title="gettext('Confirmed')">
              <i data-feather="check"></i>&nbsp;&nbsp;{{ statuses.confirmed }}
            </div>
          </div>
          <h6 class="pt-3 text-center text-secondary" v-text="gettext('Ballot Statuses')"></h6>
        </div>

      </div>
    </div>
  </div>
</template>

<script>

export default {
  props: { checks: Object, statuses: Object },
  methods: {
    widthForType: function(value, type) {
      const sumValues = obj => Object.values(obj).reduce((a, b) => a + b);
      return String(value / sumValues(type) * 100) + "%"
    }
  },
  computed: {
    checksWidths: function() {
      return {
        'checked': this.widthForType(this.checks.checked, this.checks),
        'missing': this.widthForType(this.checks.missing, this.checks),
      }
    },
    statusWidths: function() {
      return {
        'none': this.widthForType(this.statuses.none, this.statuses),
        'draft': this.widthForType(this.statuses.draft, this.statuses),
        'confirmed': this.widthForType(this.statuses.confirmed, this.statuses),
      }
    }
  }
}

</script>