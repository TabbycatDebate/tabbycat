/* Small enhancements for the server-rendered CSV wizard. */
document.addEventListener('DOMContentLoaded', () => {
  const translate = (value) => window.gettext ? window.gettext(value) : value
  const dropZone = document.getElementById('csv-drop-zone')
  if (dropZone) {
    const input = document.querySelector('#csv-upload input[type=file]')
    const selection = document.getElementById('csv-selected-files')
    let selected = []
    const updateSelection = () => {
      const transfer = new DataTransfer()
      selected.forEach((file) => transfer.items.add(file))
      input.files = transfer.files
      document.getElementById('csv-selection-card').hidden = !selected.length
      selection.replaceChildren(...selected.map((file, index) => {
        const item = document.createElement('li')
        item.className = 'list-group-item d-flex align-items-center justify-content-between'
        const name = document.createElement('span')
        name.textContent = `${file.name} · ${Math.ceil(file.size / 1024)} KB`
        const remove = document.createElement('button')
        remove.type = 'button'
        remove.className = 'btn btn-outline-secondary btn-sm ml-3'
        remove.textContent = translate('Remove')
        remove.setAttribute('aria-label', `${translate('Remove')} ${file.name}`)
        remove.addEventListener('click', () => {
          selected.splice(index, 1)
          updateSelection()
        })
        item.append(name, remove)
        return item
      }))
    }
    const addFiles = (files) => {
      for (const file of files) {
        if (!selected.some((other) => other.name === file.name && other.size === file.size && other.lastModified === file.lastModified)) selected.push(file)
      }
      updateSelection()
    }
    document.getElementById('csv-file-input').hidden = true
    input.required = false
    dropZone.addEventListener('click', () => input.click())
    document.getElementById('csv-add-files').addEventListener('click', () => input.click())
    input.addEventListener('change', () => addFiles([...input.files]))
    for (const event of ['dragover', 'drop']) dropZone.addEventListener(event, (e) => e.preventDefault())
    dropZone.addEventListener('dragover', () => dropZone.classList.add('is-dragging'))
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('is-dragging'))
    dropZone.addEventListener('drop', (event) => {
      dropZone.classList.remove('is-dragging')
      addFiles([...event.dataTransfer.files])
    })
  }

  const workspace = document.querySelector('[data-csv-workspace]')
  const panels = [...document.querySelectorAll('[data-csv-panel]')]
  if (workspace) {
    const buttons = [...workspace.querySelectorAll('[data-csv-file]')]
    const previous = workspace.querySelector('[data-file-previous]')
    const next = workspace.querySelector('[data-file-next]')
    let active = 0
    const key = 'csv-active-file:' + window.location.pathname
    const selectFile = (index) => {
      active = index
      panels.forEach((panel, i) => { panel.hidden = i !== index })
      buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)))
      previous.disabled = index === 0
      next.disabled = index === panels.length - 1
      sessionStorage.setItem(key, String(index))
    }
    buttons.forEach((button, index) => button.addEventListener('click', () => selectFile(index)))
    previous.addEventListener('click', () => selectFile(active - 1))
    next.addEventListener('click', () => selectFile(active + 1))
    workspace.querySelector('[data-file-navigation]').hidden = panels.length < 2
    const invalid = panels.findIndex((panel) => panel.querySelector('[data-status=attention], .errorlist'))
    const saved = Number(sessionStorage.getItem(key))
    selectFile(invalid >= 0 ? invalid : saved >= 0 && saved < panels.length ? saved : 0)
  }

  const previewRows = [...document.querySelectorAll('[data-csv-row]')]
  const filterPanel = (panel) => {
    const filter = panel.querySelector('[data-row-filter]')
    if (!filter) return
    const rows = [...panel.querySelectorAll('[data-csv-row]')]
    rows.forEach((row) => { row.hidden = filter.value !== 'all' && row.dataset.status !== filter.value })
    panel.querySelector('[data-empty-filter]').hidden = rows.some((row) => !row.hidden)
  }
  const updateSkip = (row) => {
    const skipped = row.querySelector('input[name$="-DELETE"]').checked
    row.dataset.status = skipped ? 'skipped' : row.dataset.invalid === 'true' ? 'attention' : 'ready'
    row.classList.toggle('text-muted', skipped)
    row.querySelectorAll('input:not([name$="-DELETE"]), select').forEach((field) => { field.disabled = skipped })
    const status = row.querySelector('[data-row-status]')
    status.textContent = translate(skipped ? 'Skipped' : row.dataset.invalid === 'true' ? 'Needs attention' : 'Ready')
    status.className = `badge ${skipped ? 'badge-secondary' : row.dataset.invalid === 'true' ? 'badge-warning' : 'badge-success'}`
    const panel = row.closest('[data-csv-panel]')
    const rows = [...panel.querySelectorAll('[data-csv-row]')]
    const attention = rows.filter((item) => item.dataset.status === 'attention').length
    const skips = rows.filter((item) => item.dataset.status === 'skipped').length
    panel.querySelector('[data-file-summary]').textContent = `${attention} ${translate('need attention')} · ${skips} ${translate('skipped')}`
    const fileStatus = document.querySelector(`[data-csv-file="${panel.dataset.csvPanel}"] [data-file-status]`)
    const badge = document.createElement('span')
    badge.className = `badge ${attention ? 'badge-warning' : 'badge-success'}`
    badge.textContent = attention ? `${attention} ${translate('need attention')}` : translate('Ready')
    fileStatus.replaceChildren(badge)
    if (skips) {
      const skipBadge = document.createElement('span')
      skipBadge.className = 'badge badge-secondary ml-1'
      skipBadge.textContent = `${skips} ${translate('skipped')}`
      fileStatus.append(skipBadge)
    }
    panel.querySelector('[data-skip-invalid]').disabled = !attention
    filterPanel(panel)
  }
  previewRows.forEach((row) => {
    row.querySelector('input[name$="-DELETE"]').addEventListener('change', () => updateSkip(row))
    updateSkip(row)
    row.querySelectorAll('input:not([name$="-DELETE"]), select').forEach((field) => {
      field.addEventListener('change', () => {
        const status = row.querySelector('[data-row-status]')
        if (row.dataset.status === 'ready') status.textContent = translate('Edited — validate to continue')
      })
    })
  })
  panels.forEach((panel) => {
    panel.querySelector('[data-row-filter]')?.addEventListener('change', () => filterPanel(panel))
    panel.querySelector('[data-skip-invalid]')?.addEventListener('click', () => {
      panel.querySelectorAll('[data-csv-row][data-invalid=true]').forEach((row) => {
        row.querySelector('input[name$="-DELETE"]').checked = true
        updateSkip(row)
      })
    })
  })
  const wizard = document.getElementById('csv-wizard')
  if (wizard && previewRows.length) {
    wizard.noValidate = true
    wizard.addEventListener('submit', () => {
      previewRows.forEach((row) => row.querySelectorAll(':disabled').forEach((field) => { field.disabled = false }))
    })
  }

  const start = document.getElementById('csv-start')
  if (start) {
    const rows = [...document.querySelectorAll('[data-result-row]')]
    const progress = document.getElementById('csv-progress')
    const updateProgress = () => {
      const completed = rows.filter((row) => row.dataset.status !== 'pending').length
      progress.textContent = `${completed} / ${rows.length}`
      document.getElementById('csv-progress-bar').value = completed
      document.querySelectorAll('[data-result-count]').forEach((count) => {
        count.textContent = rows.filter((row) => row.dataset.status === count.dataset.resultCount).length
      })
    }
    updateProgress()
    document.getElementById('csv-result-file').addEventListener('change', (event) => {
      rows.forEach((row) => { row.hidden = !!event.target.value && row.dataset.file !== event.target.value })
    })
    const storageKey = 'csv-in-flight:' + window.location.pathname
    const interrupted = () => {
      document.getElementById('csv-interrupted').hidden = false
      start.disabled = true
    }
    if (sessionStorage.getItem(storageKey)) interrupted()
    start.addEventListener('click', async () => {
      start.disabled = true
      const pending = rows.filter((row) => row.dataset.status === 'pending')
        .sort((a, b) => Number(a.dataset.priority) - Number(b.dataset.priority))
      for (const row of pending) {
        const body = new URLSearchParams({
          row: row.dataset.resultRow,
          csrfmiddlewaretoken: document.querySelector('#csv-results input[name=csrfmiddlewaretoken]').value,
        })
        try {
          sessionStorage.setItem(storageKey, row.dataset.resultRow)
          const response = await fetch(window.location.href, { method: 'POST', body, credentials: 'same-origin' })
          if (!response.ok) throw new Error('Import request failed')
          const result = await response.json()
          row.dataset.status = result.status
          row.querySelector('[data-result-status]').textContent = result.label
          row.querySelector('[data-result-errors]').textContent = result.errors
          sessionStorage.removeItem(storageKey)
          updateProgress()
        } catch (error) {
          interrupted()
          return
        }
      }
    })
    if (!rows.some((row) => row.dataset.status === 'pending')) start.disabled = true
  }
})
