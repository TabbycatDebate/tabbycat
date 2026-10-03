import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { compileScript, compileTemplate, parse } from '@vue/compiler-sfc'
import { computed, ref, toRef } from 'vue'
import _ from 'lodash'

const source = readFileSync(new URL('./CheckInStatusContainer.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const script = compileScript(descriptor, { id: 'checkins-test', genDefaultAs: 'component' })
const gettext = text => text
const tct = (text, values) => {
  let index = 0
  return text.replace(/%s/g, () => values[index++])
}

// Run the actual component setup with only its browser services stubbed.
const setup = new Function('props', '_', 'computed', 'ref', 'toRef', 'useWebSocket', 'useDjangoI18n',
  `${script.content.replace(/^import .* from .*$/gm, '')}\nreturn component.setup(props, { expose() {} })`)
const person = (id, type, extra = {}) => ({
  id, type, name: `${type} ${id}`, identifier: [`id-${id}`],
  institution: { code: 'UNI', name: 'University' }, ...extra,
})
const speaker = (id, team = 'Team A', extra = {}) => person(id, 'Speaker', { team, ...extra })
const event = id => ({ identifier: `id-${id}`, time: '2026-10-03T08:00:00Z' })
const create = (props = {}) => setup({ teamSize: 2, forAdmin: true, teamCodes: false, ...props },
  _, computed, ref, toRef, () => ({ sendToSocket() {} }), () => ({ gettext, interpolate: tct, tct }))

test('component template compiles', () => {
  const template = compileTemplate({ source: descriptor.template.content, filename: 'CheckInStatusContainer.vue', id: 'checkins-test' })
  assert.deepEqual(template.errors, [])
})

test('tooltips identify speakers and adjudicators after switching to By Person', () => {
  const view = create({ speakers: [speaker(1)], adjudicators: [person(2, 'Adjudicator')] })
  view.setListContext('speakerGroupings', 'Speaker', true)
  const tooltips = view.peopleByType.value.map(view.getToolTipForEntity)
  assert.match(tooltips[0], /an adjudicator from University/)
  assert.match(tooltips[1], /a speaker from University/)
  assert.match(view.getToolTipForEntity(person(3, 'Adjudicator', { institution: null, identifier: [null] })), /an adjudicator of no institutional affiliation with no identifier/)
  view.showCodeNames.value = true
  assert.equal(view.getToolTipForEntity(person(2, 'Adjudicator')), 'Adjudicator 2, an adjudicator')
})

test('present counts and filters include viable partial teams for two and three speakers', () => {
  for (const teamSize of [2, 3]) {
    const speakers = Array.from({ length: teamSize }, (_, index) => speaker(index + 1))
    const initialEvents = Array.from({ length: teamSize - 1 }, (_, index) => event(index + 1))
    const view = create({ teamSize, speakers, initialEvents })
    assert.equal(view.stats.value.Present, 1)
    assert.equal(view.stats.value.Absent, 0)
    view.setListContext('filterByPresence', 'Present', true)
    assert.equal(view.entitiesByPresence.value.length, 1)
    assert.match(view.getEntityStatusClass(view.annotatedTeams.value[0]), /viable-checkins-team/)
    view.events.value = []
    assert.equal(view.stats.value.Present, 0)
    assert.equal(view.entitiesByPresence.value.length, 0)
    view.setListContext('filterByPresence', 'Absent', true)
    assert.equal(view.entitiesByPresence.value.length, 1)
  }
  const view = create({ teamSize: 3, speakers: [speaker(1), speaker(2), speaker(3)], initialEvents: [event(1)] })
  assert.equal(view.stats.value.Present, 0)
  view.events.value.push(event(2), event(3))
  assert.equal(view.stats.value.Present, 1)
  assert.match(view.getEntityStatusClass(view.annotatedTeams.value[0]), /bg-success/)
})

test('copy lists absent individuals from partial teams and honours participant filters', async () => {
  const view = create({ speakers: [speaker(1), speaker(2)], adjudicators: [person(3, 'Adjudicator')], initialEvents: [event(1)] })
  assert.equal(view.absentParticipantsText.value, 'Adjudicator 3 (Adjudicator, UNI)\nSpeaker 2 (Speaker, Team A)')
  view.setListContext('filterByPresence', 'Present', true)
  assert.equal(view.absentParticipants.value.length, 2)
  view.setListContext('filterByType', 'Debaters', true)
  assert.equal(view.absentParticipantsText.value, 'Speaker 2 (Speaker, Team A)')
  view.setListContext('speakerGroupings', 'Speaker', true)
  assert.equal(view.absentParticipantsText.value, 'Speaker 2 (Speaker, Team A)')
  view.setListContext('filterByType', 'Breaking', true)
  assert.equal(view.absentParticipantsText.value, '')
  view.setListContext('filterByType', 'Adjudicators', true)
  let copied
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { clipboard: { writeText: async text => { copied = text } } } })
  await view.copyAbsentParticipants()
  assert.equal(copied, 'Adjudicator 3 (Adjudicator, UNI)')
  assert.equal(view.copyStatus.value, 'Copied absent participants.')
  globalThis.navigator.clipboard.writeText = async () => { throw new Error('Clipboard denied') }
  await view.copyAbsentParticipants()
  assert.equal(view.copyFallback.value, copied)
  assert.match(view.copyStatus.value, /Could not copy/)
})

test('hover refreshes Bootstrap cached tooltip text for the current participant', () => {
  const view = create()
  const attributes = {}
  const actions = []
  const element = {}
  const tooltip = {
    attr(name, value) { attributes[name] = value; return this },
    tooltip(action) { actions.push(action); return this },
  }
  globalThis.window = { $: target => { assert.equal(target, element); return tooltip } }
  attributes['data-original-title'] = 'Old adjudicator tooltip'
  view.showEntityTooltip({ currentTarget: element }, speaker(1))
  assert.match(attributes['data-original-title'], /a speaker from University/)
  assert.equal(actions.at(-1), 'show')
  view.hideEntityTooltip({ currentTarget: element })
  assert.equal(actions.at(-1), 'hide')
  delete globalThis.window
})
