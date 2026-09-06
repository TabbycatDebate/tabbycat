<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import DjangoFormsetManagement from '../../templates/components/DjangoFormsetManagement.vue'
import FeatherIcon from '../../templates/components/FeatherIcon.vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import ScheduleEditorEventRow from './ScheduleEditorEventRow.vue'
import { useScheduleEditor } from './useScheduleEditor.js'

const props = defineProps({ initialData: Object })
const { gettext, tct } = useDjangoI18n()
const newDayInput = ref(null)
const submitting = ref(false)
let scheduleForm = null

const {
  UNDATED_DAY,
  addDay,
  addEvent,
  automaticTitle,
  canAdd,
  dateTimeValue,
  days,
  deletedEvents,
  deleteEvent,
  dirty,
  duplicateEvent,
  duration,
  eventCountLabel,
  formatDay,
  moveEventDate,
  newDay,
  nextFormIndex,
  reorderEvent,
  reorderWithKeyboard,
  updateEvent,
  visibleEvents,
} = useScheduleEditor(props.initialData)

const displayDays = computed(() => days.value.map(day => {
  const formatted = formatDay(day.date)
  const summary = day.date === UNDATED_DAY
    ? formatted.monthYear
    : `${formatted.monthYear} · ${eventCountLabel(day.events.length)}`
  return { ...day, formatted, summary }
}))

const focusEvent = event => nextTick(() => {
  document.getElementById(`id_${props.initialData.management.prefix}-${event.formIndex}-type`)?.focus()
})

const handleAddDay = () => {
  if (!newDayInput.value?.reportValidity()) return
  const newEvent = addDay()
  if (newEvent) focusEvent(newEvent)
}

const handleAddEvent = date => {
  const event = addEvent(date)
  if (event) focusEvent(event)
}

const handleBeforeUnload = event => {
  if (!dirty.value || submitting.value) return
  event.preventDefault()
  event.returnValue = ''
}

const handleSubmit = () => {
  submitting.value = true
}

onMounted(() => {
  scheduleForm = document.getElementById('schedule-form')
  scheduleForm?.addEventListener('submit', handleSubmit)
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() => {
  scheduleForm?.removeEventListener('submit', handleSubmit)
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
</script>

<template>
  <div class="schedule-editor">
    <django-formset-management
      :management="initialData.management"
      :total-forms="nextFormIndex"
    />

    <div class="d-none">
      <template
        v-for="scheduleEvent in deletedEvents"
        :key="scheduleEvent.formIndex"
      >
        <input
          :name="`${initialData.management.prefix}-${scheduleEvent.formIndex}-id`"
          type="hidden"
          :value="scheduleEvent.id"
        >
        <input
          :name="`${initialData.management.prefix}-${scheduleEvent.formIndex}-type`"
          type="hidden"
          :value="scheduleEvent.type"
        >
        <input
          :name="`${initialData.management.prefix}-${scheduleEvent.formIndex}-title`"
          type="hidden"
          :value="scheduleEvent.title"
        >
        <input
          :name="`${initialData.management.prefix}-${scheduleEvent.formIndex}-start_time`"
          type="hidden"
          :value="dateTimeValue(scheduleEvent, 'start')"
        >
        <input
          :name="`${initialData.management.prefix}-${scheduleEvent.formIndex}-end_time`"
          type="hidden"
          :value="dateTimeValue(scheduleEvent, 'end')"
        >
        <input
          :name="`${initialData.management.prefix}-${scheduleEvent.formIndex}-round`"
          type="hidden"
          :value="scheduleEvent.round"
        >
        <input
          :name="`${initialData.management.prefix}-${scheduleEvent.formIndex}-DELETE`"
          type="hidden"
          value="on"
        >
      </template>
    </div>

    <div
      v-if="initialData.nonFormErrors.length"
      class="alert alert-danger"
    >
      <ul class="mb-0">
        <li
          v-for="error in initialData.nonFormErrors"
          :key="error"
        >
          {{ error }}
        </li>
      </ul>
    </div>

    <div class="card mb-3">
      <div class="card-body d-flex flex-wrap justify-content-between align-items-center py-3">
        <div class="mb-2 mb-md-0">
          <strong>{{ eventCountLabel(visibleEvents.length) }}</strong>
          <span class="text-muted ml-2">
            <feather-icon
              class="mr-1"
              name="clock"
            />
            {{ tct('Times shown in %s', [initialData.timezoneLabel]) }}
          </span>
          <span
            v-if="dirty"
            class="text-warning ml-2"
          >{{ gettext('Unsaved changes.') }}</span>
        </div>
        <div
          v-if="initialData.canEdit"
          class="schedule-add-day d-flex align-items-center"
        >
          <label
            class="sr-only"
            for="schedule-new-day"
          >{{ gettext('New schedule day') }}</label>
          <input
            id="schedule-new-day"
            ref="newDayInput"
            v-model="newDay"
            class="form-control mr-2"
            type="date"
            form="schedule-add-day-form"
            required
          >
          <button
            class="btn btn-primary text-nowrap"
            type="button"
            :disabled="!canAdd"
            @click="handleAddDay"
          >
            <feather-icon
              class="mr-1"
              name="calendar"
            />{{ gettext('Add day') }}
          </button>
        </div>
      </div>
    </div>

    <section
      v-for="day in displayDays"
      :key="day.date"
      class="card schedule-day mb-3"
    >
      <header class="card-header schedule-day-header d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
          <span class="schedule-date-tile">{{ day.formatted.number }}</span>
          <div>
            <strong class="d-block">{{ day.formatted.weekday }}</strong>
            <small class="text-muted">{{ day.summary }}</small>
          </div>
        </div>
        <button
          v-if="initialData.canEdit && day.date !== UNDATED_DAY"
          class="btn btn-outline-primary btn-sm"
          type="button"
          @click="handleAddEvent(day.date)"
        >
          <feather-icon
            class="mr-1"
            name="plus"
          />{{ gettext('Add event') }}
        </button>
      </header>

      <div
        class="schedule-grid-header d-none d-xl-flex"
        aria-hidden="true"
      >
        <span class="schedule-drag-column" />
        <div class="row flex-grow-1 mx-0">
          <span class="col-xl-2">{{ gettext('Start') }}</span>
          <span class="col-xl-2">{{ gettext('End') }}</span>
          <span class="col-xl-2">{{ gettext('Event type') }}</span>
          <span class="col-xl-3">{{ gettext('Custom title') }} <small>{{ gettext('optional') }}</small></span>
          <span class="col-xl-2">{{ gettext('Round') }}</span>
          <span class="col-xl-1">{{ gettext('Duration') }}</span>
        </div>
        <span class="schedule-actions-column" />
      </div>

      <schedule-editor-event-row
        v-for="scheduleEvent in day.events"
        :key="scheduleEvent.formIndex"
        :event="scheduleEvent"
        :day-date="day.date"
        :can-edit="initialData.canEdit"
        :prefix="initialData.management.prefix"
        :type-choices="initialData.typeChoices"
        :round-choices="initialData.roundChoices"
        :automatic-title="automaticTitle(scheduleEvent)"
        :duration="duration(scheduleEvent)"
        :start-date-time="dateTimeValue(scheduleEvent, 'start')"
        :end-date-time="dateTimeValue(scheduleEvent, 'end')"
        @delete-event="deleteEvent"
        @duplicate-event="duplicateEvent"
        @move-date="moveEventDate"
        @reorder="reorderEvent"
        @reorder-keyboard="reorderWithKeyboard"
        @update-event="updateEvent"
      />
    </section>

    <div
      v-if="displayDays.length === 0"
      class="card text-center"
    >
      <div class="card-body py-5">
        <feather-icon
          class="schedule-empty-icon"
          name="calendar"
        />
        <h5 class="mt-3">
          {{ gettext('No schedule events yet') }}
        </h5>
        <p class="text-muted mb-0">
          {{ gettext('Choose a date above to start building the schedule.') }}
        </p>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "bootstrap/scss/functions";
@import "../../templates/scss/components/custom";
@import "bootstrap/scss/variables";
@import "bootstrap/scss/mixins/breakpoints";

.schedule-add-day input {
  min-width: 170px;
}

.schedule-day {
  overflow: hidden;
}

.schedule-day-header {
  min-height: 64px;
  background: $white;
}

.schedule-date-tile {
  width: 42px;
  height: 42px;
  margin-right: 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: $border-radius;
  color: darken(theme-color("info"), 22%);
  background: lighten(theme-color("info"), 38%);
  font-size: 1.25rem;
  font-weight: $font-weight-bold;
}

.schedule-grid-header {
  padding: 0.6rem 0;
  color: $text-muted;
  background: $gray-100;
  border-bottom: 1px solid $gray-300;
  font-size: $font-size-sm;
  font-weight: $font-weight-bold;
  text-transform: uppercase;
}

.schedule-drag-column {
  flex: 0 0 34px;
}

.schedule-actions-column {
  flex: 0 0 96px;
}

.schedule-empty-icon :deep(.feather) {
  width: 34px;
  height: 34px;
  margin: 0;
  color: $gray-500;
}

@include media-breakpoint-down(sm) {

  .schedule-add-day {
    width: 100%;
    margin-top: 0.75rem;
  }

  .schedule-add-day input {
    min-width: 0;
  }

  .schedule-day-header .btn {
    padding-right: 0.5rem;
    padding-left: 0.5rem;
    font-size: 0;
  }

  .schedule-day-header .btn :deep(.feather) {
    margin: 0;
  }
}
</style>
