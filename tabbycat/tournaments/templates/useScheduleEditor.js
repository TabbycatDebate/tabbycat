import { computed, ref } from 'vue'
import { useDjangoFormset } from '../../templates/composables/useDjangoFormset.js'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

const UNDATED_DAY = '__undated__'

export function useScheduleEditor (initialData) {
  const { gettext, ngettext, tct } = useDjangoI18n()
  const locale = document.documentElement.lang || undefined
  const normalizeEvent = event => ({
    ...event,
    errors: { ...event.errors },
    nonFieldErrors: [...event.nonFieldErrors],
  })
  const {
    addForm,
    canAdd,
    deletedForms: deletedEvents,
    deleteForm,
    fieldName,
    findForm: findEvent,
    nextFormIndex,
    visibleForms: visibleEvents,
  } = useDjangoFormset(initialData.events, initialData.management, normalizeEvent)
  const newDay = ref('')
  const dirty = ref(false)

  const dateTimeValue = (event, kind) => {
    const raw = event[`${kind}Raw`]
    if (raw !== null) {
      return raw
    }
    const date = event[`${kind}Date`]
    const time = event[`${kind}Time`]
    return date && time ? `${date}T${time}` : ''
  }

  const eventSortValue = event => dateTimeValue(event, 'start') || `${event.startDate}T99:99`

  const days = computed(() => {
    const grouped = new Map()
    visibleEvents.value.forEach(event => {
      const key = event.startDate || UNDATED_DAY
      if (!grouped.has(key)) {
        grouped.set(key, [])
      }
      grouped.get(key).push(event)
    })

    return Array.from(grouped.entries())
      .sort(([left], [right]) => {
        if (left === UNDATED_DAY) return 1
        if (right === UNDATED_DAY) return -1
        return left.localeCompare(right)
      })
      .map(([date, dayEvents]) => ({
        date,
        events: dayEvents.sort((left, right) => {
          const timeComparison = eventSortValue(left).localeCompare(eventSortValue(right))
          return timeComparison || left.formIndex - right.formIndex
        }),
      }))
  })

  const choiceLabel = (choices, value) => choices.find(choice => String(choice[0]) === String(value))?.[1] || ''

  const automaticTitle = event => {
    const round = event.round ? choiceLabel(initialData.roundChoices, event.round) : ''
    const type = choiceLabel(initialData.typeChoices, event.type)
    return [round, type].filter(Boolean).join(' — ') || gettext('Untitled event')
  }

  const localDate = date => new Date(`${date}T12:00:00`)

  const dayFormatter = new Intl.DateTimeFormat(locale, { day: 'numeric' })
  const weekdayFormatter = new Intl.DateTimeFormat(locale, { weekday: 'long' })
  const monthYearFormatter = new Intl.DateTimeFormat(locale, { month: 'long', year: 'numeric' })

  const formatDay = date => {
    if (date === UNDATED_DAY) {
      return {
        number: '?',
        weekday: gettext('Needs a date'),
        monthYear: gettext('Correct the start time below'),
      }
    }
    const value = localDate(date)
    return {
      number: dayFormatter.format(value),
      weekday: weekdayFormatter.format(value),
      monthYear: monthYearFormatter.format(value),
    }
  }

  const duration = event => {
    const start = dateTimeValue(event, 'start')
    const end = dateTimeValue(event, 'end')
    if (!start || !end || event.startRaw !== null || event.endRaw !== null) {
      return { label: '—', invalid: false }
    }
    const minutes = Math.round((new Date(end) - new Date(start)) / 60000)
    if (minutes <= 0) {
      return { label: gettext('Check time'), invalid: true }
    }
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    const parts = []
    if (hours) parts.push(tct('%s h', [hours]))
    if (remainingMinutes) parts.push(tct('%s min', [remainingMinutes]))
    return { label: parts.join(' '), invalid: false }
  }

  const eventCountLabel = count => {
    const format = ngettext('%s event', '%s events', count)
    return window.interpolate(format, [count])
  }

  const markDirty = () => {
    dirty.value = true
  }

  const clearFieldErrors = (event, field) => {
    if (event.errors[field]) {
      delete event.errors[field]
    }
  }

  const updateEvent = (formIndex, field, value) => {
    const event = findEvent(formIndex)
    if (!event) return
    event[field] = value
    if (field === 'startTime') {
      event.startRaw = null
      clearFieldErrors(event, 'start_time')
    } else if (field === 'endTime') {
      event.endRaw = null
      if (value && !event.endDate) event.endDate = event.startDate
      clearFieldErrors(event, 'end_time')
    } else {
      clearFieldErrors(event, field)
    }
    event.nonFieldErrors = []
    markDirty()
  }

  const moveEventDate = (formIndex, date) => {
    const event = findEvent(formIndex)
    if (!event || !date) return
    event.startDate = date
    event.startRaw = null
    if (event.endTime) event.endDate = date
    event.endRaw = null
    clearFieldErrors(event, 'start_time')
    clearFieldErrors(event, 'end_time')
    event.nonFieldErrors = []
    markDirty()
  }

  const nextStartTime = date => {
    const day = days.value.find(item => item.date === date)
    const lastEvent = day?.events.at(-1)
    return lastEvent?.endTime || lastEvent?.startTime || '09:00'
  }

  const makeEvent = (date, source = null) => ({
    id: '',
    type: source?.type || initialData.defaultEventType,
    title: source?.title || '',
    startDate: source?.startDate || date,
    startTime: source?.startTime || nextStartTime(date),
    startRaw: null,
    endDate: source?.endDate || date,
    endTime: source?.endTime || '',
    endRaw: null,
    round: source?.round || '',
    errors: {},
    nonFieldErrors: [],
  })

  const addEvent = date => {
    if (!initialData.canEdit || !canAdd.value || !date || date === UNDATED_DAY) return null
    const event = addForm(makeEvent(date))
    markDirty()
    return event
  }

  const addDay = () => {
    if (!newDay.value) return null
    return addEvent(newDay.value)
  }

  const duplicateEvent = formIndex => {
    const source = findEvent(formIndex)
    if (!source || !canAdd.value) return
    addForm(makeEvent(source.startDate, source))
    markDirty()
  }

  const deleteEvent = formIndex => {
    const event = deleteForm(formIndex)
    if (!event) return
    markDirty()
  }

  const reorderEvent = (sourceIndex, targetIndex, placeAfter) => {
    const source = findEvent(sourceIndex)
    const target = findEvent(targetIndex)
    if (!source || !target || source === target || source.startDate !== target.startDate) return
    const day = days.value.find(item => item.date === source.startDate)
    const ordered = [...day.events]
    const slots = ordered.map(event => ({
      startDate: event.startDate,
      startTime: event.startTime,
      endDate: event.endDate,
      endTime: event.endTime,
    }))
    ordered.splice(ordered.indexOf(source), 1)
    const targetPosition = ordered.indexOf(target) + (placeAfter ? 1 : 0)
    ordered.splice(targetPosition, 0, source)
    ordered.forEach((event, index) => {
      Object.assign(event, slots[index], { startRaw: null, endRaw: null, nonFieldErrors: [] })
      clearFieldErrors(event, 'start_time')
      clearFieldErrors(event, 'end_time')
    })
    markDirty()
  }

  const reorderWithKeyboard = (formIndex, direction) => {
    const event = findEvent(formIndex)
    const day = days.value.find(item => item.date === event?.startDate)
    if (!event || !day) return
    const index = day.events.indexOf(event)
    const target = day.events[index + direction]
    if (target) reorderEvent(formIndex, target.formIndex, direction > 0)
  }

  return {
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
    fieldName,
    formatDay,
    moveEventDate,
    newDay,
    nextFormIndex,
    reorderEvent,
    reorderWithKeyboard,
    updateEvent,
    visibleEvents,
    canEdit: initialData.canEdit,
    roundChoices: initialData.roundChoices,
    typeChoices: initialData.typeChoices,
  }
}
