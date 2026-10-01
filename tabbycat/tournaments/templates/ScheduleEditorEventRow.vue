<script setup>
import { computed, ref } from 'vue'
import FeatherIcon from '../../templates/components/FeatherIcon.vue'
import FormFieldErrors from '../../templates/components/FormFieldErrors.vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { useDraggable } from '../../templates/composables/useDraggable.js'

const props = defineProps({
  event: Object,
  dayDate: String,
  editor: Object,
})

const { gettext } = useDjangoI18n()
const {
  automaticTitle: getAutomaticTitle,
  canEdit,
  dateTimeValue,
  deleteEvent,
  duplicateEvent,
  duration: getDuration,
  fieldName: getFieldName,
  moveEventDate,
  reorderEvent,
  reorderWithKeyboard,
  roundChoices,
  typeChoices,
  updateEvent,
} = props.editor
const dateInput = ref(null)
const dropPosition = ref(null)
const fieldName = field => getFieldName(props.event.formIndex, field)
const fieldId = field => `id_${fieldName(field)}`
const fieldErrors = field => props.event.errors[field] || []
const automaticTitle = computed(() => getAutomaticTitle(props.event))
const duration = computed(() => getDuration(props.event))
const startDateTime = computed(() => dateTimeValue(props.event, 'start'))
const endDateTime = computed(() => dateTimeValue(props.event, 'end'))

const dragOptions = {
  locked: !canEdit,
  get dragPayload () {
    return { formIndex: props.event.formIndex, dayDate: props.dayDate }
  },
}
const { isDragging, dragStart, dragEnd } = useDraggable(dragOptions)

const rowClasses = computed(() => ({
  'schedule-row-dragging': isDragging.value,
  'schedule-row-drop-before': dropPosition.value === 'before',
  'schedule-row-drop-after': dropPosition.value === 'after',
}))

const update = (field, value) => updateEvent(props.event.formIndex, field, value)

const openDatePicker = () => {
  if (typeof dateInput.value?.showPicker === 'function') {
    dateInput.value.showPicker()
  } else {
    dateInput.value?.click()
  }
}

const onDragStart = event => {
  dragStart(event)
  event.dataTransfer.effectAllowed = 'move'
}

const onDragOver = event => {
  const dataTypes = Array.from(event.dataTransfer.types)
  if (!dataTypes.includes('text') && !dataTypes.includes('text/plain')) return
  event.preventDefault()
  const midpoint = event.currentTarget.getBoundingClientRect().top + event.currentTarget.offsetHeight / 2
  dropPosition.value = event.clientY > midpoint ? 'after' : 'before'
  event.dataTransfer.dropEffect = 'move'
}

const onDragLeave = event => {
  if (!event.currentTarget.contains(event.relatedTarget)) dropPosition.value = null
}

const onDrop = event => {
  event.preventDefault()
  try {
    const payload = JSON.parse(event.dataTransfer.getData('text'))
    if (payload.dayDate === props.dayDate) {
      reorderEvent(payload.formIndex, props.event.formIndex, dropPosition.value === 'after')
    }
  } catch {}
  dropPosition.value = null
}

const onKeyboardReorder = event => {
  if (!['ArrowUp', 'ArrowDown'].includes(event.key)) return
  event.preventDefault()
  reorderWithKeyboard(props.event.formIndex, event.key === 'ArrowUp' ? -1 : 1)
}
</script>

<template>
  <div
    class="schedule-event-row d-flex align-items-stretch"
    :class="rowClasses"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <div class="schedule-event-hidden">
      <input
        :name="fieldName('id')"
        type="hidden"
        :value="event.id"
      >
      <input
        :name="fieldName('start_time')"
        type="hidden"
        :value="startDateTime"
      >
      <input
        :name="fieldName('end_time')"
        type="hidden"
        :value="endDateTime"
      >
      <input
        v-if="canEdit"
        :name="fieldName('DELETE')"
        type="hidden"
        :value="event.deleted ? 'on' : ''"
      >
    </div>

    <button
      v-if="canEdit"
      class="schedule-drag-handle"
      type="button"
      draggable="true"
      :title="gettext('Drag to reorder')"
      :aria-label="gettext('Drag to reorder; use arrow keys for keyboard reordering')"
      @dragstart="onDragStart"
      @dragend="dragEnd"
      @keydown="onKeyboardReorder"
    >
      <feather-icon name="menu" />
    </button>
    <span
      v-else
      class="schedule-drag-column"
    />

    <div class="schedule-event-fields row flex-grow-1 mx-0">
      <div class="schedule-field form-group col-6 col-md-3 col-xl-2">
        <label :for="fieldId('start_time_control')">{{ gettext('Start') }}</label>
        <input
          :id="fieldId('start_time_control')"
          class="form-control schedule-time-control"
          :class="{ 'is-invalid': fieldErrors('start_time').length }"
          type="time"
          step="60"
          :value="event.startTime"
          :required="canEdit"
          :disabled="!canEdit"
          :aria-invalid="fieldErrors('start_time').length > 0"
          :aria-label="gettext('Start time')"
          @input="update('startTime', $event.target.value)"
        >
        <form-field-errors :errors="fieldErrors('start_time')" />
      </div>

      <div class="schedule-field form-group col-6 col-md-3 col-xl-2">
        <label :for="fieldId('end_time_control')">{{ gettext('End') }}</label>
        <input
          :id="fieldId('end_time_control')"
          class="form-control schedule-time-control"
          :class="{ 'is-invalid': fieldErrors('end_time').length }"
          type="time"
          step="60"
          :value="event.endTime"
          :disabled="!canEdit"
          :aria-invalid="fieldErrors('end_time').length > 0"
          :aria-label="gettext('End time')"
          @input="update('endTime', $event.target.value)"
        >
        <form-field-errors :errors="fieldErrors('end_time')" />
      </div>

      <div class="schedule-field form-group col-12 col-md-3 col-xl-2">
        <label :for="fieldId('type')">{{ gettext('Event type') }}</label>
        <select
          :id="fieldId('type')"
          class="form-control"
          :class="{ 'is-invalid': fieldErrors('type').length }"
          :name="fieldName('type')"
          :value="event.type"
          :disabled="!canEdit"
          :aria-label="gettext('Event type')"
          :aria-invalid="fieldErrors('type').length > 0"
          @change="update('type', $event.target.value)"
        >
          <option
            v-for="choice in typeChoices"
            :key="choice[0]"
            :value="choice[0]"
          >
            {{ choice[1] }}
          </option>
        </select>
        <form-field-errors :errors="fieldErrors('type')" />
      </div>

      <div class="schedule-field form-group col-12 col-md-6 col-xl-3 order-md-5 order-xl-4">
        <label :for="fieldId('title')">
          {{ gettext('Custom title') }} <span class="text-muted font-weight-normal">({{ gettext('optional') }})</span>
        </label>
        <input
          :id="fieldId('title')"
          class="form-control"
          :class="{ 'is-invalid': fieldErrors('title').length }"
          :name="fieldName('title')"
          type="text"
          maxlength="100"
          :value="event.title"
          :disabled="!canEdit"
          :placeholder="automaticTitle"
          :aria-label="gettext('Custom title')"
          :aria-invalid="fieldErrors('title').length > 0"
          @input="update('title', $event.target.value)"
        >
        <small class="schedule-title-hint text-muted">
          {{ gettext('Leave blank to show') }} “<strong>{{ automaticTitle }}</strong>”
        </small>
        <form-field-errors :errors="fieldErrors('title')" />
      </div>

      <div class="schedule-field form-group col-12 col-md-6 col-xl-2 order-md-6 order-xl-5">
        <label :for="fieldId('round')">{{ gettext('Round') }}</label>
        <select
          :id="fieldId('round')"
          class="form-control"
          :class="{ 'is-invalid': fieldErrors('round').length }"
          :name="fieldName('round')"
          :value="event.round"
          :disabled="!canEdit"
          :aria-label="gettext('Round')"
          :aria-invalid="fieldErrors('round').length > 0"
          @change="update('round', $event.target.value)"
        >
          <option
            v-for="choice in roundChoices"
            :key="choice[0]"
            :value="choice[0]"
          >
            {{ choice[1] }}
          </option>
        </select>
        <form-field-errors :errors="fieldErrors('round')" />
      </div>

      <div
        class="schedule-duration col-12 col-md-3 col-xl-1 order-md-4 order-xl-6"
        :class="{ 'text-danger': duration.invalid }"
      >
        <span class="d-xl-none font-weight-bold text-muted">{{ gettext('Duration') }}: </span>
        {{ duration.label }}
      </div>

      <div
        v-if="event.nonFieldErrors.length"
        class="schedule-row-errors col-12 order-last"
      >
        <form-field-errors :errors="event.nonFieldErrors" />
      </div>
    </div>

    <div
      v-if="canEdit"
      class="schedule-row-actions"
    >
      <span class="schedule-row-date-control">
        <button
          class="btn btn-link p-1"
          type="button"
          :title="gettext('Move to another day')"
          :aria-label="gettext('Move to another day')"
          @click="openDatePicker"
        >
          <feather-icon name="calendar" />
        </button>
        <input
          ref="dateInput"
          type="date"
          tabindex="-1"
          aria-hidden="true"
          :value="event.startDate"
          @change="moveEventDate(event.formIndex, $event.target.value)"
        >
      </span>
      <button
        class="btn btn-link p-1"
        type="button"
        :title="gettext('Duplicate event')"
        :aria-label="gettext('Duplicate event')"
        @click="duplicateEvent(event.formIndex)"
      >
        <feather-icon name="copy" />
      </button>
      <button
        class="btn btn-link text-danger p-1"
        type="button"
        :title="gettext('Delete event')"
        :aria-label="gettext('Delete event')"
        @click="deleteEvent(event.formIndex)"
      >
        <feather-icon name="trash-2" />
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "bootstrap/scss/functions";
@import "../../templates/scss/components/custom";
@import "bootstrap/scss/variables";
@import "bootstrap/scss/mixins/breakpoints";
@import "../../templates/scss/components/variables";

.schedule-event-row {
  position: relative;
  background: $white;
  border-bottom: 1px solid $gray-200;
  transition: background-color 120ms ease, opacity 120ms ease;
}

.schedule-event-row:last-child {
  border-bottom: 0;
}

.schedule-event-row:hover {
  background: $gray-100;
}

.schedule-event-fields {
  min-width: 0;
  padding: 0.7rem 0.35rem 0;
}

.schedule-event-hidden {
  display: none;
}

.schedule-field {
  min-width: 0;
}

.schedule-field .form-control {
  min-width: 0;
}

.schedule-title-hint {
  margin-top: 0.28rem;
  display: block;
  overflow: hidden;
  color: $text-muted;
  font-size: 0.72rem;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.schedule-title-hint strong {
  color: $gray-700;
  font-weight: $font-weight-normal;
}

.schedule-time-control,
.schedule-duration {
  font-variant-numeric: tabular-nums;
}

.schedule-drag-column,
.schedule-drag-handle {
  flex: 0 0 34px;
}

.schedule-drag-handle {
  width: 34px;
  padding: 0;
  border: 0;
  border-radius: 0;
  color: $gray-600;
  background: transparent;
  cursor: move;
}

.schedule-drag-handle:hover,
.schedule-drag-handle:focus {
  color: $white;
  background: theme-color("primary");
  outline: 0;
}

.schedule-drag-handle :deep(.feather) {
  margin: 0;
}

.schedule-row-dragging {
  opacity: 0.55;
}

.schedule-row-drop-before::before,
.schedule-row-drop-after::after {
  position: absolute;
  left: 0.75rem;
  right: 0.75rem;
  z-index: $z_2;
  height: 4px;
  border-radius: 2px;
  background: theme-color("success");
  content: "";
}

.schedule-row-drop-before::before {
  top: -2px;
}

.schedule-row-drop-after::after {
  bottom: -2px;
}

.schedule-row-actions {
  flex: 0 0 96px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 0.5rem;
}

.schedule-row-actions :deep(.feather) {
  width: 17px;
  height: 17px;
}

.schedule-row-date-control {
  position: relative;
  display: inline-block;
}

.schedule-row-date-control input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.schedule-duration {
  color: $text-muted;
  white-space: nowrap;
}

@include media-breakpoint-up(xl) {

  .schedule-event-row label {
    display: none;
  }

  .schedule-duration {
    padding-top: 0.55rem;
  }
}

@include media-breakpoint-down(sm) {

  .schedule-drag-column,
  .schedule-drag-handle {
    flex-basis: 28px;
  }

  .schedule-row-actions {
    flex-basis: 36px;
    flex-direction: column;
    justify-content: center;
    padding-right: 0;
  }
}
</style>
