import assert from 'node:assert/strict'
import test from 'node:test'
import { useScheduleEditor } from './useScheduleEditor.js'

globalThis.document = { documentElement: { lang: 'en' } }
globalThis.window = {
  gettext: value => value,
  ngettext: (singular, plural, count) => count === 1 ? singular : plural,
  interpolate: (format, values) => format.replace('%s', values[0]),
}

const event = (formIndex, startTime, endTime = '') => ({
  formIndex,
  id: String(formIndex + 1),
  type: 'D',
  title: '',
  startDate: '2026-08-15',
  startTime,
  startRaw: null,
  endDate: '2026-08-15',
  endTime,
  endRaw: null,
  round: '1',
  deleted: false,
  errors: {},
  nonFieldErrors: [],
})

const initialData = events => ({
  events,
  management: {
    totalForms: events.length,
    initialForms: events.length,
    minNumForms: 0,
    maxNumForms: 1000,
  },
  typeChoices: [['D', 'Debate'], ['O', 'Other']],
  roundChoices: [['', '---------'], ['1', 'Round 1']],
  defaultEventType: 'O',
  canEdit: true,
})

test('groups events by date and keeps invalid dates in a correction group', () => {
  const invalid = { ...event(2, ''), startDate: '', startRaw: 'not-a-date' }
  const editor = useScheduleEditor(initialData([
    event(0, '10:00'),
    { ...event(1, '09:00'), startDate: '2026-08-16', endDate: '2026-08-16' },
    invalid,
  ]))

  assert.deepEqual(editor.days.value.map(day => day.date), [
    '2026-08-15',
    '2026-08-16',
    editor.UNDATED_DAY,
  ])
})

test('adds, duplicates, and deletes forms with stable indices', () => {
  const editor = useScheduleEditor(initialData([event(0, '09:00', '10:00')]))

  const added = editor.addEvent('2026-08-15')
  editor.duplicateEvent(0)
  editor.deleteEvent(0)

  assert.equal(added.formIndex, 1)
  assert.equal(added.startTime, '10:00')
  assert.deepEqual(editor.visibleEvents.value.map(item => item.formIndex), [1, 2])
  assert.deepEqual(editor.deletedEvents.value.map(item => item.formIndex), [0])
  assert.equal(editor.nextFormIndex.value, 3)
})

test('reordering moves events into the destination time slots', () => {
  const editor = useScheduleEditor(initialData([
    event(0, '09:00', '10:00'),
    event(1, '10:00', '11:00'),
  ]))

  editor.reorderEvent(0, 1, true)

  assert.equal(editor.visibleEvents.value[0].startTime, '10:00')
  assert.equal(editor.visibleEvents.value[1].startTime, '09:00')
  assert.deepEqual(editor.days.value[0].events.map(item => item.formIndex), [1, 0])
})

test('calculates cross-midnight durations and flags reversed times', () => {
  const overnight = { ...event(0, '23:30', '00:30'), endDate: '2026-08-16' }
  const reversed = event(1, '11:00', '10:00')
  const editor = useScheduleEditor(initialData([overnight, reversed]))

  assert.deepEqual(editor.duration(overnight), { label: '1 h', invalid: false })
  assert.deepEqual(editor.duration(reversed), { label: 'Check time', invalid: true })
})

test('editing an invalid value clears its raw value and field error', () => {
  const invalid = {
    ...event(0, ''),
    startRaw: 'not-a-date',
    errors: { start_time: ['Enter a valid date/time.'] },
  }
  const editor = useScheduleEditor(initialData([invalid]))

  editor.updateEvent(0, 'startTime', '09:00')
  const updated = editor.visibleEvents.value[0]

  assert.equal(updated.startRaw, null)
  assert.deepEqual(updated.errors, {})
  assert.equal(editor.dirty.value, true)
})
