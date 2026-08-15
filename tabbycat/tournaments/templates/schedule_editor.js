import feather from 'feather-icons'

const initializeScheduleEditor = (root) => {
  const form = root.querySelector('#schedule-form')
  const daysContainer = root.querySelector('[data-schedule-days]')
  const emptyFormTemplate = root.querySelector('#schedule-empty-form-template')
  const dayTemplate = root.querySelector('#schedule-day-template')
  const totalForms = form.querySelector('[name$="-TOTAL_FORMS"]')
  const canEdit = root.dataset.canEdit === 'true'
  let draggedRow = null
  let toastTimeout = null

  const visibleRows = (container = root) => Array.from(container.querySelectorAll('[data-schedule-row]'))
    .filter(row => !row.classList.contains('d-none'))

  const field = (row, suffix) => row.querySelector(`[name$="-${suffix}"]`)

  root.classList.add('schedule-enhanced')

  const showToast = (message) => {
    const toast = root.querySelector('[data-schedule-toast]')
    toast.textContent = message
    toast.classList.add('show')
    window.clearTimeout(toastTimeout)
    toastTimeout = window.setTimeout(() => toast.classList.remove('show'), 2200)
  }

  const markDirty = () => {
    const state = root.querySelector('[data-save-state]')
    if (state) {
      state.classList.remove('text-muted')
      state.classList.add('text-warning')
    }
  }

  const parseDateTime = (value) => value ? new Date(value) : null

  const durationLabel = (row) => {
    const start = parseDateTime(field(row, 'start_time').value)
    const end = parseDateTime(field(row, 'end_time').value)
    if (!start || !end) {
      return { label: '—', invalid: false }
    }
    const minutes = Math.round((end - start) / 60000)
    if (minutes <= 0) {
      return { label: root.dataset.invalidTimeLabel, invalid: true }
    }
    const hours = Math.floor(minutes / 60)
    const remaining = minutes % 60
    const label = hours > 0
      ? `${hours}h${remaining > 0 ? ` ${remaining}m` : ''}`
      : `${remaining}m`
    return { label, invalid: false }
  }

  const updateDuration = (row) => {
    const output = row.querySelector('[data-duration]')
    const duration = durationLabel(row)
    output.textContent = duration.label
    output.classList.toggle('text-danger', duration.invalid)
  }

  const syncTimeControls = (row) => {
    const startSource = field(row, 'start_time')
    const endSource = field(row, 'end_time')
    row.querySelector('[data-time-control="start"]').value = startSource.value.slice(11, 16)
    row.querySelector('[data-time-control="end"]').value = endSource.value.slice(11, 16)
    const dateInput = row.querySelector('[data-row-date]')
    if (dateInput) {
      dateInput.value = startSource.value.slice(0, 10) || row.closest('[data-schedule-day]')?.dataset.date || ''
    }
  }

  const updateSourceTime = (row, sourceSuffix, timeValue) => {
    const source = field(row, sourceSuffix)
    if (!timeValue) {
      source.value = ''
      return
    }
    const currentDate = source.value.slice(0, 10)
    const dayDate = row.closest('[data-schedule-day]')?.dataset.date || ''
    source.value = `${currentDate || dayDate}T${timeValue}`
  }

  const updateSourceDate = (source, dateString) => {
    if (!source.value) {
      return
    }
    source.value = `${dateString}${source.value.slice(10)}`
  }

  const formatDay = (dateString) => {
    const date = new Date(`${dateString}T12:00:00`)
    return {
      number: new Intl.DateTimeFormat(undefined, { day: 'numeric' }).format(date),
      weekday: new Intl.DateTimeFormat(undefined, { weekday: 'long' }).format(date),
      monthYear: new Intl.DateTimeFormat(undefined, { month: 'long', year: 'numeric' }).format(date),
      full: new Intl.DateTimeFormat(undefined, {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      }).format(date),
    }
  }

  const updateDay = (day) => {
    const rows = visibleRows(day)
    const dateString = day.dataset.date
    const summary = day.querySelector('[data-day-summary]')
    if (dateString) {
      const formatted = formatDay(dateString)
      day.querySelector('[data-day-number]').textContent = formatted.number
      day.querySelector('[data-day-weekday]').textContent = formatted.weekday
      const eventWord = rows.length === 1 ? root.dataset.eventLabel : root.dataset.eventsLabel
      summary.textContent = `${formatted.monthYear} · ${rows.length} ${eventWord}`
    }
    day.querySelector('[data-day-empty]').classList.toggle('d-none', rows.length > 0)
  }

  const updateCounts = () => {
    const count = visibleRows().length
    const eventWord = count === 1 ? root.dataset.eventLabel : root.dataset.eventsLabel
    root.querySelector('[data-schedule-count]').textContent = `${count} ${eventWord}`
    root.querySelector('[data-schedule-empty]').classList.toggle('d-none', root.querySelectorAll('[data-schedule-day]').length > 0)
    root.querySelectorAll('[data-schedule-day]').forEach(updateDay)
  }

  const formatTime = (value) => {
    const date = parseDateTime(value)
    if (!date) {
      return '—'
    }
    return new Intl.DateTimeFormat(undefined, { hour: '2-digit', minute: '2-digit' }).format(date)
  }

  const automaticTitle = (row) => {
    const typeSelect = field(row, 'type')
    const roundSelect = field(row, 'round')
    const typeLabel = typeSelect.options[typeSelect.selectedIndex]?.text || ''
    const roundLabel = roundSelect.options[roundSelect.selectedIndex]?.text || ''
    return [typeLabel, roundSelect.value ? roundLabel : ''].filter(Boolean).join(' — ') || root.dataset.untitledLabel
  }

  const updateTitleState = (row) => {
    const titleInput = field(row, 'title')
    const usesAutomaticTitle = titleInput.value.trim() === ''
    const generatedTitle = automaticTitle(row)
    row.querySelector('[data-automatic-title]').textContent = generatedTitle
    row.querySelector('[data-automatic-title-state]').classList.toggle('d-none', !usesAutomaticTitle)
    titleInput.placeholder = generatedTitle
    titleInput.classList.toggle('schedule-title-is-automatic', usesAutomaticTitle)
  }

  const updatePreview = () => {
    const preview = root.querySelector('[data-schedule-preview]')
    preview.replaceChildren()
    Array.from(daysContainer.querySelectorAll('[data-schedule-day]')).forEach(day => {
      const rows = visibleRows(day)
      if (rows.length === 0 || !day.dataset.date) {
        return
      }
      const heading = document.createElement('h5')
      heading.className = 'schedule-preview-date'
      heading.textContent = formatDay(day.dataset.date).full
      preview.appendChild(heading)

      rows.forEach(row => {
        const item = document.createElement('div')
        item.className = 'schedule-preview-event'

        const time = document.createElement('div')
        time.className = 'schedule-preview-time'
        const start = field(row, 'start_time').value
        const end = field(row, 'end_time').value
        time.textContent = end ? `${formatTime(start)}–${formatTime(end)}` : formatTime(start)

        const details = document.createElement('div')
        const title = document.createElement('strong')
        const customTitle = field(row, 'title').value.trim()
        title.textContent = customTitle || automaticTitle(row)
        const meta = document.createElement('small')
        meta.className = 'd-block text-muted'
        const typeSelect = field(row, 'type')
        const roundSelect = field(row, 'round')
        const typeLabel = typeSelect.options[typeSelect.selectedIndex]?.text || ''
        const roundLabel = roundSelect.options[roundSelect.selectedIndex]?.text || ''
        meta.textContent = roundSelect.value ? `${typeLabel} · ${roundLabel}` : typeLabel
        meta.classList.toggle('d-none', customTitle === '')

        details.append(title, meta)
        item.append(time, details)
        preview.appendChild(item)
      })
    })
  }

  const refresh = () => {
    visibleRows().forEach(row => {
      updateDuration(row)
      updateTitleState(row)
    })
    updateCounts()
    updatePreview()
  }

  const insertDayInOrder = (day) => {
    const datedDays = Array.from(daysContainer.querySelectorAll('[data-schedule-day][data-date]:not([data-date=""])'))
    const nextDay = datedDays.find(existing => existing.dataset.date > day.dataset.date)
    if (nextDay) {
      daysContainer.insertBefore(day, nextDay)
    } else {
      daysContainer.appendChild(day)
    }
  }

  const createDay = (dateString) => {
    let day = daysContainer.querySelector(`[data-schedule-day][data-date="${dateString}"]`)
    if (day || !dayTemplate) {
      return day
    }
    day = dayTemplate.content.firstElementChild.cloneNode(true)
    day.dataset.date = dateString
    insertDayInOrder(day)
    activateDay(day)
    updateDay(day)
    return day
  }

  const nextStartTime = (day) => {
    const rows = visibleRows(day)
    if (rows.length === 0) {
      return `${day.dataset.date}T09:00`
    }
    const lastRow = rows[rows.length - 1]
    return field(lastRow, 'end_time').value || field(lastRow, 'start_time').value
  }

  const createRow = (day) => {
    if (!emptyFormTemplate || !totalForms) {
      return null
    }
    const index = Number(totalForms.value)
    const markup = emptyFormTemplate.innerHTML.replace(/__prefix__/g, index)
    const wrapper = document.createElement('div')
    wrapper.innerHTML = markup.trim()
    const row = wrapper.firstElementChild
    totalForms.value = index + 1
    field(row, 'start_time').value = nextStartTime(day)
    field(row, 'end_time').value = ''
    day.querySelector('[data-schedule-rows]').appendChild(row)
    activateRow(row)
    syncTimeControls(row)
    feather.replace()
    markDirty()
    refresh()
    return row
  }

  const copyRowValues = (source, target) => {
    const copiedFields = ['start_time', 'end_time', 'type', 'title', 'round']
    copiedFields.forEach(suffix => {
      field(target, suffix).value = field(source, suffix).value
    })
    target.dataset.eventType = field(target, 'type').value
    syncTimeControls(target)
  }

  const removeRow = (row) => {
    const deleteInput = field(row, 'DELETE')
    if (deleteInput) {
      deleteInput.value = 'on'
    }
    row.querySelectorAll('[data-time-control]').forEach(control => {
      control.disabled = true
    })
    row.classList.add('d-none')
    markDirty()
    refresh()
    showToast(root.dataset.deletedLabel)
  }

  const timeSlots = (rows) => rows.map(row => ({
    start: field(row, 'start_time').value,
    end: field(row, 'end_time').value,
  }))

  const assignTimeSlots = (rows, slots) => {
    rows.forEach((row, index) => {
      field(row, 'start_time').value = slots[index].start
      field(row, 'end_time').value = slots[index].end
      syncTimeControls(row)
    })
  }

  const moveRowIntoSlot = (row, target, placeAfter) => {
    if (row === target || row.closest('[data-schedule-day]') !== target.closest('[data-schedule-day]')) {
      return
    }
    const day = row.closest('[data-schedule-day]')
    const rowsBeforeMove = visibleRows(day)
    const slots = timeSlots(rowsBeforeMove)
    if (placeAfter) {
      target.after(row)
    } else {
      target.before(row)
    }
    assignTimeSlots(visibleRows(day), slots)
    markDirty()
    refresh()
    showToast(root.dataset.draggedLabel)
    row.querySelector('[data-drag-handle]').focus()
  }

  const clearDropTargets = () => {
    root.querySelectorAll('.schedule-row-drop-before, .schedule-row-drop-after').forEach(row => {
      row.classList.remove('schedule-row-drop-before', 'schedule-row-drop-after')
    })
  }

  const scrollDuringDrag = (event) => {
    const threshold = 100
    if (event.clientY < threshold) {
      window.scrollBy(0, -12)
    } else if (event.clientY > window.innerHeight - threshold) {
      window.scrollBy(0, 12)
    }
  }

  const moveRowToMatchingDay = (row) => {
    const dateString = field(row, 'start_time').value.slice(0, 10)
    const currentDay = row.closest('[data-schedule-day]')
    if (!dateString || dateString === currentDay.dataset.date) {
      return
    }
    const targetDay = createDay(dateString)
    targetDay.querySelector('[data-schedule-rows]').appendChild(row)
    const sortedRows = visibleRows(targetDay).sort((a, b) =>
      field(a, 'start_time').value.localeCompare(field(b, 'start_time').value))
    sortedRows.forEach(sortedRow => targetDay.querySelector('[data-schedule-rows]').appendChild(sortedRow))
  }

  const activateRow = (row) => {
    const startSource = field(row, 'start_time')
    const startControl = row.querySelector('[data-time-control="start"]')
    const endControl = row.querySelector('[data-time-control="end"]')
    startSource.required = false
    startControl.required = canEdit
    startControl.disabled = !canEdit
    endControl.disabled = !canEdit
    syncTimeControls(row)

    row.querySelectorAll('input, select').forEach(control => {
      control.addEventListener('input', () => {
        if (control === field(row, 'type')) {
          row.dataset.eventType = control.value
        }
        updateDuration(row)
        updateTitleState(row)
        updatePreview()
        markDirty()
      })
    })

    startControl.addEventListener('input', () => {
      updateSourceTime(row, 'start_time', startControl.value)
      updateDuration(row)
      updatePreview()
      markDirty()
    })
    endControl.addEventListener('input', () => {
      updateSourceTime(row, 'end_time', endControl.value)
      updateDuration(row)
      updatePreview()
      markDirty()
    })

    field(row, 'start_time').addEventListener('change', () => {
      moveRowToMatchingDay(row)
      refresh()
    })

    row.querySelector('[data-row-date]')?.addEventListener('change', event => {
      updateSourceDate(field(row, 'start_time'), event.target.value)
      updateSourceDate(field(row, 'end_time'), event.target.value)
      moveRowToMatchingDay(row)
      refresh()
      markDirty()
    })
    row.querySelector('[data-move-event-day]')?.addEventListener('click', () => {
      const dateInput = row.querySelector('[data-row-date]')
      if (dateInput.showPicker) {
        dateInput.showPicker()
      } else {
        dateInput.click()
      }
    })

    const duplicateButton = row.querySelector('[data-duplicate-event]')
    duplicateButton?.addEventListener('click', () => {
      const duplicate = createRow(row.closest('[data-schedule-day]'))
      copyRowValues(row, duplicate)
      row.after(duplicate)
      refresh()
      showToast(root.dataset.duplicatedLabel)
    })

    row.querySelector('[data-delete-event]')?.addEventListener('click', () => removeRow(row))

    const handle = row.querySelector('[data-drag-handle]')
    if (!handle) {
      return
    }
    handle.addEventListener('dragstart', event => {
      draggedRow = row
      row.classList.add('schedule-row-dragging')
      event.dataTransfer.effectAllowed = 'move'
      event.dataTransfer.setData('text/plain', field(row, 'id')?.value || '')
      event.dataTransfer.setDragImage(row, 20, 20)
      window.addEventListener('dragover', scrollDuringDrag)
    })
    handle.addEventListener('dragend', () => {
      row.classList.remove('schedule-row-dragging')
      draggedRow = null
      clearDropTargets()
      window.removeEventListener('dragover', scrollDuringDrag)
    })
    handle.addEventListener('keydown', event => {
      if (!['ArrowUp', 'ArrowDown'].includes(event.key)) {
        return
      }
      const rows = visibleRows(row.closest('[data-schedule-day]'))
      const index = rows.indexOf(row)
      const target = event.key === 'ArrowUp' ? rows[index - 1] : rows[index + 1]
      if (target) {
        event.preventDefault()
        moveRowIntoSlot(row, target, event.key === 'ArrowDown')
      }
    })

    row.addEventListener('dragover', event => {
      if (!draggedRow || draggedRow.closest('[data-schedule-day]') !== row.closest('[data-schedule-day]')) {
        return
      }
      event.preventDefault()
      clearDropTargets()
      const placeAfter = event.clientY > row.getBoundingClientRect().top + row.offsetHeight / 2
      row.classList.add(placeAfter ? 'schedule-row-drop-after' : 'schedule-row-drop-before')
      event.dataTransfer.dropEffect = 'move'
    })
    row.addEventListener('drop', event => {
      if (!draggedRow) {
        return
      }
      event.preventDefault()
      const placeAfter = event.clientY > row.getBoundingClientRect().top + row.offsetHeight / 2
      moveRowIntoSlot(draggedRow, row, placeAfter)
      clearDropTargets()
    })
  }

  function activateDay (day) {
    day.querySelector('[data-add-event]')?.addEventListener('click', () => {
      const row = createRow(day)
      field(row, 'type').focus()
    })
  }

  root.querySelectorAll('[data-schedule-row]').forEach(activateRow)
  root.querySelectorAll('[data-schedule-day]').forEach(activateDay)

  root.querySelector('[data-add-day]')?.addEventListener('click', () => {
    const input = root.querySelector('#schedule-new-day')
    if (!input.value) {
      input.reportValidity()
      return
    }
    const day = createDay(input.value)
    const row = createRow(day)
    field(row, 'type').focus()
  })

  root.querySelectorAll('[data-schedule-mode]').forEach(button => {
    button.addEventListener('click', () => {
      const mode = button.dataset.scheduleMode
      root.querySelectorAll('[data-schedule-mode]').forEach(candidate => {
        const active = candidate === button
        candidate.classList.toggle('active', active)
        candidate.classList.toggle('btn-secondary', active)
        candidate.classList.toggle('btn-outline-secondary', !active)
      })
      root.querySelectorAll('[data-schedule-panel]').forEach(panel => {
        panel.classList.toggle('d-none', panel.dataset.schedulePanel !== mode)
      })
      root.querySelector('.schedule-save-bar')?.classList.toggle('d-none', mode !== 'edit')
      if (mode === 'preview') {
        updatePreview()
      }
    })
  })

  refresh()
}

const scheduleEditor = document.getElementById('schedule-editor')
if (scheduleEditor) {
  initializeScheduleEditor(scheduleEditor)
}
