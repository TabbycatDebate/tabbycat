import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileScript, compileTemplate, parse } from '@vue/compiler-sfc'
import { computed, ref, toRef, watch } from 'vue'
import _ from 'lodash'
import { useCheckboxSelection } from '../composables/useCheckboxSelection.js'
import { useSortableTable } from '../composables/useSortableTable.js'

function component (filename, props, services = {}, emit = () => {}) {
  const source = readFileSync(new URL(filename, import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  assert.deepEqual(compileTemplate({ source: descriptor.template.content, filename, id: filename }).errors, [])
  const script = compileScript(descriptor, { id: filename, genDefaultAs: 'component' })
  const dependencies = {
    _, computed, ref, toRef, watch, onBeforeUnmount() {}, defineAsyncComponent: () => ({}),
    useCheckboxSelection, useSortableTable, useDjangoI18n: () => ({ gettext: text => text }),
    SmartHeader: {}, SmartCell: {}, CheckCell: {}, AjaxSelectCell: {}, BallotsCell: {},
    ...services,
  }
  const setup = new Function(...Object.keys(dependencies), 'props', 'emit',
    `${script.content.replace(/^import .* from .*$/gm, '')}\nreturn component.setup(props, { expose() {}, emit })`)
  return setup(...Object.values(dependencies), props, emit)
}

const checkbox = extra => ({ component: 'check-cell', checked: false, type: 0, ...extra })

function table (cells, save = () => {}) {
  const events = []
  const view = component('./SmartTable.vue', { tableHeaders: [{ key: 'check' }], tableContent: cells.map(cell => [cell]) }, {},
    (...event) => events.push(event))
  for (const cell of cells) {
    const instance = component('./CheckCell.vue', { cellData: cell }, { useAjax: () => ({ ajaxSave: save }) },
      (...event) => events.push(event))
    view.setCellRef(cell, instance)
  }
  return { view, events }
}

test('bulk updates use final category state, preserve form-only changes, and save individual cells', () => {
  const cells = [checkbox({ id: 1 }), checkbox({ id: 2 }), checkbox({ noSave: true }),
    checkbox({ saveURL: '/save', id: 4 }), checkbox({ disabled: true }), checkbox({ checked: true })]
  const saves = []
  const { view, events } = table(cells, (...args) => saves.push(args))
  view.start(cells.map(cell => [cell]), 0, 0)
  view.extend(5, 0)
  view.setSelected(true)
  assert.deepEqual(cells.map(cell => cell.checked), [true, true, true, true, false, true])
  assert.equal(events.filter(([name]) => name === 'toggle-checked').length, 1)
  assert.equal(saves.length, 1)
  assert.deepEqual(saves[0][1], { id: 4, 0: true })
  assert.equal(view.selected.value.size, 0)
  view.start(cells.map(cell => [cell]), 0, 0)
  view.extend(3, 0)
  view.setSelected(false)
  assert.deepEqual(cells.map(cell => cell.checked), [false, false, false, false, false, true])
})

test('mouse drags select without toggling and suppress the release click; normal clicks still work', () => {
  const cells = [checkbox(), checkbox()]
  const { view } = table(cells)
  const listeners = new Map()
  const root = Object.freeze({ focus() {} })
  view.tableElement.value = root
  const target = row => ({ closest: selector => selector === 'td[data-row]'
    ? { dataset: { row, column: 0 }, closest: () => root } : null })
  globalThis.window = {
    addEventListener: (name, handler) => listeners.set(name, handler),
    removeEventListener: name => listeners.delete(name),
  }
  globalThis.document = { elementFromPoint: () => target(1) }
  try {
    const event = { button: 0, pointerType: 'mouse', pointerId: 1, clientX: 0, clientY: 0, target: target(0) }
    view.beginSelection(event)
    listeners.get('pointerup')(event)
    let prevented = false
    const click = { preventDefault: () => { prevented = true }, stopPropagation() {} }
    view.preventDragClick(click)
    assert.equal(prevented, false)
    view.beginSelection(event)
    listeners.get('pointermove')({ ...event, clientY: 40, preventDefault() {} })
    listeners.get('pointerup')(event)
    view.preventDragClick(click)
    assert.equal(prevented, true)
    assert.equal(view.selected.value.size, 2)
    assert.ok(cells.every(cell => !cell.checked))
    assert.equal(listeners.size, 0)
  } finally {
    delete globalThis.window
    delete globalThis.document
  }
})

test('Space checks mixed selections, unchecks fully checked selections, and ignores repeats and other controls', () => {
  const cells = [checkbox(), checkbox({ checked: true }), checkbox({ noSave: true })]
  const { view, events } = table(cells)
  view.start(cells.map(cell => [cell]), 0, 0)
  view.extend(2, 0)
  const root = Object.freeze({})
  view.tableElement.value = root
  let prevented = 0
  const event = { target: root, repeat: false, preventDefault: () => { prevented++ } }
  view.toggleSelectedWithSpace(event)
  assert.deepEqual(cells.map(cell => cell.checked), [true, true, true])
  assert.equal(view.selected.value.size, 3)
  assert.equal(events.filter(([name]) => name === 'toggle-checked').length, 1)
  view.toggleSelectedWithSpace({ ...event, repeat: true })
  assert.deepEqual(cells.map(cell => cell.checked), [true, true, true])
  view.toggleSelectedWithSpace({ ...event, target: { matches: () => false } })
  assert.equal(prevented, 2, 'buttons and text fields keep their normal Space behavior')
  view.toggleSelectedWithSpace({ ...event, target: { matches: () => true } })
  assert.deepEqual(cells.map(cell => cell.checked), [false, false, false])
  view.toggleSelectedWithSpace(event)
  assert.deepEqual(cells.map(cell => cell.checked), [true, true, true], 'Space checks an entirely unchecked selection')
  assert.equal(view.selected.value.size, 3)
  view.clear()
  view.toggleSelectedWithSpace(event)
  assert.equal(prevented, 4, 'Space without a selection keeps its normal behavior')
})
