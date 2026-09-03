<script setup>
import feather from 'feather-icons'
import { computed } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import ScheduleEditorEventRow from './ScheduleEditorEventRow.vue'

const props = defineProps({
  day: Object,
  undatedDay: String,
  canEdit: Boolean,
  prefix: String,
  typeChoices: Array,
  roundChoices: Array,
  automaticTitle: Function,
  dateTimeValue: Function,
  duration: Function,
  eventCountLabel: Function,
  formatDay: Function,
})

const emit = defineEmits([
  'add-event',
  'delete-event',
  'duplicate-event',
  'move-date',
  'reorder',
  'reorder-keyboard',
  'update-event',
])

const { gettext } = useDjangoI18n()
const formattedDay = computed(() => props.formatDay(props.day.date))
const daySummary = computed(() => props.day.date === props.undatedDay
  ? formattedDay.value.monthYear
  : `${formattedDay.value.monthYear} · ${props.eventCountLabel(props.day.events.length)}`)
const icon = name => feather.icons[name].toSvg()
</script>

<template>
  <section class="card schedule-day mb-3">
    <header class="card-header schedule-day-header d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center">
        <span class="schedule-date-tile">{{ formattedDay.number }}</span>
        <div>
          <strong class="d-block">{{ formattedDay.weekday }}</strong>
          <small class="text-muted">{{ daySummary }}</small>
        </div>
      </div>
      <button
        v-if="canEdit && day.date !== undatedDay"
        class="btn btn-outline-primary btn-sm"
        type="button"
        @click="emit('add-event', day.date)"
      >
        <span v-html="icon('plus')" />{{ gettext('Add event') }}
      </button>
    </header>

    <div
      class="schedule-grid-header"
      aria-hidden="true"
    >
      <span />
      <span>{{ gettext('Start') }}</span>
      <span>{{ gettext('End') }}</span>
      <span>{{ gettext('Event type') }}</span>
      <span>{{ gettext('Custom title') }} <small>{{ gettext('optional') }}</small></span>
      <span>{{ gettext('Round') }}</span>
      <span>{{ gettext('Duration') }}</span>
      <span />
    </div>

    <schedule-editor-event-row
      v-for="scheduleEvent in day.events"
      :key="scheduleEvent.formIndex"
      :event="scheduleEvent"
      :day-date="day.date"
      :can-edit="canEdit"
      :prefix="prefix"
      :type-choices="typeChoices"
      :round-choices="roundChoices"
      :automatic-title="automaticTitle(scheduleEvent)"
      :duration="duration(scheduleEvent)"
      :start-date-time="dateTimeValue(scheduleEvent, 'start')"
      :end-date-time="dateTimeValue(scheduleEvent, 'end')"
      @delete-event="(...args) => emit('delete-event', ...args)"
      @duplicate-event="(...args) => emit('duplicate-event', ...args)"
      @move-date="(...args) => emit('move-date', ...args)"
      @reorder="(...args) => emit('reorder', ...args)"
      @reorder-keyboard="(...args) => emit('reorder-keyboard', ...args)"
      @update-event="(...args) => emit('update-event', ...args)"
    />
  </section>
</template>
