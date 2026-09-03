<script setup>
import feather from 'feather-icons'
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import TablesContainer from '../../templates/tables/TablesContainer.vue'
import ScheduleEditorDay from './ScheduleEditorDay.vue'
import { useScheduleEditor } from './useScheduleEditor.js'

const props = defineProps({
  initialData: Object,
})

const { gettext, tct } = useDjangoI18n()
const newDayInput = ref(null)
const icon = name => feather.icons[name].toSvg()
const {
  UNDATED_DAY,
  addDay,
  addEvent,
  automaticTitle,
  beginSubmit,
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
  mode,
  moveEventDate,
  newDay,
  nextFormIndex,
  previewTables,
  reorderEvent,
  reorderWithKeyboard,
  submitting,
  toast,
  updateEvent,
  visibleEvents,
} = useScheduleEditor(props.initialData)

const focusEvent = event => nextTick(() => {
  document.getElementById(`id_${props.initialData.management.prefix}-${event.formIndex}-type`)?.focus()
})

const handleAddDay = () => {
  if (!newDay.value) {
    newDayInput.value?.setCustomValidity(gettext('Choose a date before adding a schedule day.'))
    newDayInput.value?.reportValidity()
    return
  }
  newDayInput.value?.setCustomValidity('')
  const event = addDay()
  if (event) focusEvent(event)
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

onMounted(() => window.addEventListener('beforeunload', handleBeforeUnload))
onBeforeUnmount(() => window.removeEventListener('beforeunload', handleBeforeUnload))
</script>

<template>
  <div class="schedule-editor">
    <input
      :name="`${initialData.management.prefix}-TOTAL_FORMS`"
      type="hidden"
      :value="nextFormIndex"
    >
    <input
      :name="`${initialData.management.prefix}-INITIAL_FORMS`"
      type="hidden"
      :value="initialData.management.initialForms"
    >
    <input
      :name="`${initialData.management.prefix}-MIN_NUM_FORMS`"
      type="hidden"
      :value="initialData.management.minNumForms"
    >
    <input
      :name="`${initialData.management.prefix}-MAX_NUM_FORMS`"
      type="hidden"
      :value="initialData.management.maxNumForms"
    >
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
          :name="`${initialData.management.prefix}-${scheduleEvent.formIndex}-tournament`"
          type="hidden"
          :value="scheduleEvent.tournament"
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

    <div class="d-lg-flex justify-content-between align-items-start mb-3">
      <div>
        <p class="mb-1">
          {{ gettext('Build the public tournament schedule. Events are grouped by day and ordered by start time.') }}
        </p>
        <small class="text-muted">
          {{ gettext("Drag an event into another row's time slot to reorder it. Start and end times follow the slot.") }}
        </small>
      </div>
      <div
        class="btn-group schedule-mode-switch mt-3 mt-lg-0"
        role="group"
        :aria-label="gettext('Schedule view')"
      >
        <button
          class="btn"
          :class="mode === 'edit' ? 'btn-secondary active' : 'btn-outline-secondary'"
          type="button"
          @click="mode = 'edit'"
        >
          <span v-html="icon('edit-3')" />{{ gettext('Edit schedule') }}
        </button>
        <button
          class="btn"
          :class="mode === 'preview' ? 'btn-secondary active' : 'btn-outline-secondary'"
          type="button"
          @click="mode = 'preview'"
        >
          <span v-html="icon('eye')" />{{ gettext('Public preview') }}
        </button>
      </div>
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

    <section v-show="mode === 'edit'">
      <div class="card schedule-toolbar mb-3">
        <div class="card-body d-flex flex-wrap justify-content-between align-items-center py-3">
          <div class="mb-2 mb-md-0">
            <strong>{{ eventCountLabel(visibleEvents.length) }}</strong>
            <span class="text-muted ml-2">
              <span v-html="icon('clock')" />
              {{ tct('Times shown in %s', [initialData.timezoneLabel]) }}
            </span>
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
              @input="$event.target.setCustomValidity('')"
            >
            <button
              class="btn btn-primary text-nowrap"
              type="button"
              :disabled="!canAdd"
              @click="handleAddDay"
            >
              <span v-html="icon('calendar')" />{{ gettext('Add day') }}
            </button>
          </div>
        </div>
      </div>

      <schedule-editor-day
        v-for="day in days"
        :key="day.date"
        :day="day"
        :undated-day="UNDATED_DAY"
        :can-edit="initialData.canEdit"
        :prefix="initialData.management.prefix"
        :type-choices="initialData.typeChoices"
        :round-choices="initialData.roundChoices"
        :automatic-title="automaticTitle"
        :date-time-value="dateTimeValue"
        :duration="duration"
        :event-count-label="eventCountLabel"
        :format-day="formatDay"
        @add-event="handleAddEvent"
        @delete-event="deleteEvent"
        @duplicate-event="duplicateEvent"
        @move-date="moveEventDate"
        @reorder="reorderEvent"
        @reorder-keyboard="reorderWithKeyboard"
        @update-event="updateEvent"
      />

      <div
        v-if="days.length === 0"
        class="schedule-empty card text-center"
      >
        <div class="card-body py-5">
          <span
            class="schedule-empty-icon"
            v-html="icon('calendar')"
          />
          <h5 class="mt-3">
            {{ gettext('No schedule events yet') }}
          </h5>
          <p class="text-muted mb-0">
            {{ gettext('Choose a date above to start building the schedule.') }}
          </p>
        </div>
      </div>
    </section>

    <section v-show="mode === 'preview'">
      <div class="card schedule-preview">
        <div class="card-body p-lg-4">
          <h4 class="mb-1">
            {{ gettext('Tournament Schedule') }}
          </h4>
          <p class="text-muted">
            {{ gettext('Preview of the schedule participants will see.') }}
          </p>
          <tables-container
            v-if="previewTables.length"
            :tables-data="previewTables"
            orientation="rows"
          />
          <p
            v-else
            class="text-muted mb-0"
          >
            {{ gettext('No schedule events yet') }}
          </p>
        </div>
      </div>
    </section>

    <div
      v-if="initialData.canEdit && mode === 'edit'"
      class="schedule-save-bar"
    >
      <span :class="dirty ? 'text-warning' : 'text-muted'">
        {{ dirty ? gettext('Unsaved changes.') : gettext('Changes are not saved automatically.') }}
      </span>
      <button
        class="btn btn-success"
        type="submit"
        name="submit"
        @click="beginSubmit"
      >
        <span v-html="icon('save')" />{{ gettext('Save Schedule') }}
      </button>
    </div>

    <div
      class="schedule-toast"
      :class="{ show: toast }"
      role="status"
      aria-live="polite"
    >
      {{ toast }}
    </div>
  </div>
</template>
