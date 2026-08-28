export function useModalError () {
  const showErrorAlert = (message, error, title,
    classOverride = false, titleOverride = false, messageOverride = false) => {
    const modalEl = document.getElementById('modalAlert')
    if (!modalEl) return

    const bs = window.bootstrap
    bs.Modal.getOrCreateInstance(modalEl).show()

    const header = modalEl.querySelector('.modal-header')
    const body = modalEl.querySelector('.modal-body')

    if (title === null) {
      header.textContent = 'Save Failed'
    } else if (titleOverride) {
      header.textContent = title
    } else {
      header.textContent = `Save Failed due to ${title}`
    }
    if (classOverride) {
      header.classList.remove('text-danger')
      header.classList.add(classOverride)
    } else {
      header.classList.add('text-danger')
    }
    if (messageOverride) {
      body.textContent = message
    } else {
      body.textContent = `Failed to save a change to ${message} because
          ${error}. You should now refresh this page to ensure the data is up to date and then
          retry the action. If the problem persists please get in touch with the developers.`
    }
  }

  return { showErrorAlert }
}
