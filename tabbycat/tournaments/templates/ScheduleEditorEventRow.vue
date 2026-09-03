<script setup>
import feather from 'feather-icons'
import { computed, ref } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import { useDraggable } from '../../templates/composables/useDraggable.js'

const props = defineProps({
  event: Object,
  dayDate: String,
  canEdit: Boolean,
  prefix: String,
  typeChoices: Array,
  roundChoices: Array,
  automaticTitle: String,
  duration: Object,
  startDateTime: String,
  endDateTime: String,
})

const emit = defineEmits([
  'delete-event',
  'duplicate-event',
  'move-date',
  'reorder',
  'reorder-keyboard',
  'update-event',
])

const { gettext } = useDjangoI18n()
const dateInput = ref(null)
const dropPosition = ref(null)
const fieldName = field => `${props.prefix}-${props.event.formIndex}-${field}`
const fieldId = field => `id_${fieldName(field)}`
const fieldErrors = field => props.event.errors[field] || []
const icon = name => feather.icons[name].toSvg()

const dragOptions = {
  get locked () { return !props.canEdit },
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

const update = (field, value) => emit('update-event', props.event.formIndex, field, value)

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
      emit('reorder', payload.formIndex, props.event.formIndex, dropPosition.value === 'after')
    }
  } catch {}
  dropPosition.value = null
}

const onKeyboardReorder = event => {
  if (!['ArrowUp', 'ArrowDown'].includes(event.key)) return
  event.preventDefault()
  emit('reorder-keyboard', props.event.formIndex, event.key === 'ArrowUp' ? -1 : 1)
}
</script>

<template>
  <div
    v-show="!event.deleted"
    class="schedule-event-row"
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
        :name="fieldName('tournament')"
        type="hidden"
        :value="event.tournament"
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
      <span v-html="icon('menu')" />
    </button>
    <span v-else />

    <div class="schedule-field schedule-field-start">
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
      <ul
        v-if="fieldErrors('start_time').length"
        class="errorlist"
      >
        <li
          v-for="error in fieldErrors('start_time')"
          :key="error"
        >
          {{ error }}
        </li>
      </ul>
    </div>

    <div class="schedule-field schedule-field-end">
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
      <ul
        v-if="fieldErrors('end_time').length"
        class="errorlist"
      >
        <li
          v-for="error in fieldErrors('end_time')"
          :key="error"
        >
          {{ error }}
        </li>
      </ul>
    </div>

    <div class="schedule-field schedule-field-type">
      <label :for="fieldId('type')">{{ gettext('Event type') }}</label>
      <select
        :id="fieldId('type')"
        class="form-control"
        :class="{ 'is-invalid': fieldErrors('type').length }"
        :name="fieldName('type')"
        :value="event.type"
        :disabled="!canEdit"
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
      <ul
        v-if="fieldErrors('type').length"
        class="errorlist"
      >
        <li
          v-for="error in fieldErrors('type')"
          :key="error"
        >
          {{ error }}
        </li>
      </ul>
    </div>

    <div class="schedule-field schedule-field-title">
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
        :aria-invalid="fieldErrors('title').length > 0"
        @input="update('title', $event.target.value)"
      >
      <small class="schedule-title-hint text-muted">
        {{ gettext('Leave blank to show') }} “<strong>{{ automaticTitle }}</strong>”
      </small>
      <ul
        v-if="fieldErrors('title').length"
        class="errorlist"
      >
        <li
          v-for="error in fieldErrors('title')"
          :key="error"
        >
          {{ error }}
        </li>
      </ul>
    </div>

    <div class="schedule-field schedule-field-round">
      <label :for="fieldId('round')">{{ gettext('Round') }}</label>
      <select
        :id="fieldId('round')"
        class="form-control"
        :class="{ 'is-invalid': fieldErrors('round').length }"
        :name="fieldName('round')"
        :value="event.round"
        :disabled="!canEdit"
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
      <ul
        v-if="fieldErrors('round').length"
        class="errorlist"
      >
        <li
          v-for="error in fieldErrors('round')"
          :key="error"
        >
          {{ error }}
        </li>
      </ul>
    </div>

    <div
      class="schedule-duration"
      :class="{ 'text-danger': duration.invalid }"
    >
      {{ duration.label }}
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
          <span v-html="icon('calendar')" />
        </button>
        <input
          ref="dateInput"
          type="date"
          tabindex="-1"
          aria-hidden="true"
          :value="event.startDate"
          @change="emit('move-date', event.formIndex, $event.target.value)"
        >
      </span>
      <button
        class="btn btn-link p-1"
        type="button"
        :title="gettext('Duplicate event')"
        :aria-label="gettext('Duplicate event')"
        @click="emit('duplicate-event', event.formIndex)"
      >
        <span v-html="icon('copy')" />
      </button>
      <button
        class="btn btn-link text-danger p-1"
        type="button"
        :title="gettext('Delete event')"
        :aria-label="gettext('Delete event')"
        @click="emit('delete-event', event.formIndex)"
      >
        <span v-html="icon('trash-2')" />
      </button>
    </div>

    <div
      v-if="event.nonFieldErrors.length"
      class="schedule-row-errors"
    >
      <ul class="errorlist">
        <li
          v-for="error in event.nonFieldErrors"
          :key="error"
        >
          {{ error }}
        </li>
      </ul>
    </div>
  </div>
</template>
