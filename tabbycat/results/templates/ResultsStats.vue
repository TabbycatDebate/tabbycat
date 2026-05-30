<script setup>
import { computed } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

const props = defineProps({ checks: Object, statuses: Object })

const { gettext } = useDjangoI18n()

const widthForType = (value, type) => {
  const sumValues = obj => (Object.values(obj).reduce((a, b) => a + b) || 1)
  return `${value / sumValues(type) * 100}%`
}

const checksWidths = computed(() => {
  return {
    checked: widthForType(props.checks.checked, props.checks),
    missing: widthForType(props.checks.missing, props.checks),
  }
})

const statusWidths = computed(() => {
  return {
    none: widthForType(props.statuses.none, props.statuses),
    postponed: widthForType(props.statuses.postponed, props.statuses),
    draft: widthForType(props.statuses.draft, props.statuses),
    confirmed: widthForType(props.statuses.confirmed, props.statuses),
  }
})
</script>

<template>
  <div class="card-deck">
    <div class="card mb-3">
      <div class="card-body text-center pb-1 row">
        <div class="col">
          <div class="progress">
            <div
              class="progress-bar bg-secondary"
              role="progressbar"
              :style="{ width: checksWidths.checked }"
              data-toggle="tooltip"
              :title="checks.checked + ' ' + gettext('Checked-In')"
            >
              <i data-feather="x" />&nbsp;&nbsp;{{ checks.checked }}
            </div>
            <div
              class="progress-bar bg-dark"
              role="progressbar"
              :style="{ width: checksWidths.missing }"
              data-toggle="tooltip"
              :title="checks.missing + ' ' + gettext('Not Checked-In')"
            >
              <i data-feather="circle" />&nbsp;&nbsp;{{ checks.missing }}
            </div>
          </div>
          <h6 class="pt-3 text-center text-secondary">
            {{ gettext('Ballot Check-Ins') }}
          </h6>
        </div>

        <div class="col">
          <div class="progress">
            <div
              class="progress-bar bg-danger"
              role="progressbar"
              :style="{ width: statusWidths.none }"
              data-toggle="tooltip"
              :title="statuses.none + ' ' + gettext('Unknown')"
            >
              <i data-feather="x" />&nbsp;&nbsp;{{ statuses.none }}
            </div>
            <div
              class="progress-bar bg-warning"
              role="progressbar"
              :style="{ width: statusWidths.postponed }"
              data-toggle="tooltip"
              :title="statuses.postponed + ' ' + gettext('Postponed')"
            >
              <i data-feather="pause" />&nbsp;&nbsp;{{ statuses.postponed }}
            </div>
            <div
              class="progress-bar bg-info"
              role="progressbar"
              :style="{ width: statusWidths.draft }"
              data-toggle="tooltip"
              :title="statuses.draft + ' ' + gettext('Unconfirmed')"
            >
              <i data-feather="circle" />&nbsp;&nbsp;{{ statuses.draft }}
            </div>
            <div
              class="progress-bar bg-success"
              role="progressbar"
              :style="{ width: statusWidths.confirmed }"
              data-toggle="tooltip"
              :title="statuses.confirmed + ' ' + gettext('Confirmed')"
            >
              <i data-feather="check" />&nbsp;&nbsp;{{ statuses.confirmed }}
            </div>
          </div>
          <h6 class="pt-3 text-center text-secondary">
            {{ gettext('Ballot Statuses') }}
          </h6>
        </div>
      </div>
    </div>
  </div>
</template>
