import { useCookie } from './useCookie.js'
import { useModalError } from './useModalError.js'

export function useAjax (onSaveSuccess) {
  const { getCookie } = useCookie()
  const { showErrorAlert } = useModalError()

  const ajaxError = (message, responseText, textStatus, errorThrown) => {
    let error = 'of a server error'
    let errorTitle = errorThrown
    if (errorThrown === '' || typeof (responseText) === 'undefined') {
      errorTitle = 'Server Error'
    }

    if (errorThrown === 'timeout') {
      error = `the server did not respond in time. This could be because your
                 internet access is slow/unreliable, or the server is under
                 heavy load`
      errorTitle = 'Connection Timeout'
    } else if (typeof (responseText) === 'undefined') {
      error = `the server did not respond. Perhaps your internet connection
                 was lost or the server is under heavy load or otherwise offline`
      errorTitle = 'Connection Failure'
    } else {
      try {
        const response = JSON.parse(responseText)
        if (typeof (response.message) !== 'undefined') {
          error = response.message
        }
      } catch (e) {
        errorTitle = 'Unknown Error'
        console.error(message, '//', responseText, '//', textStatus, '//', errorThrown)
      }
    }

    showErrorAlert(message, error, errorTitle)
  }

  const ajaxSave = (
    url, payload, message, completeFunction, failFunction,
    returnPayload, showErrorModal = true,
  ) => {
    const $ = window.$ || window.jQuery
    if (!$) {
      throw new Error('jQuery is required for ajaxSave')
    }

    const dataPayload = JSON.stringify(payload)
    const csrftoken = getCookie('csrftoken')

    $.ajax({
      type: 'POST',
      url: url,
      headers: { 'X-CSRFToken': csrftoken },
      mode: 'same-origin',
      data: dataPayload,
      contentType: 'application/json',
      dataType: 'json',
      error: function (hxr, textStatus, errorThrown) {
        if (showErrorModal === true) {
          ajaxError(message, hxr.responseText, textStatus, errorThrown)
        }
        if (failFunction !== null) {
          failFunction(payload, returnPayload)
        }
      },
      success: function (data) {
        if (JSON.parse(data).status === 503) {
          this.error('', '', '503 Service Unavailable')
        } else {
          if (onSaveSuccess) {
            onSaveSuccess(new Date())
          }
          console.debug(`AJAX: Saved ${message}`)
          console.debug('DEBUG: JSON ajaxSave success data:', data)
          const dataResponse = JSON.parse(data)
          if (completeFunction !== null) {
            completeFunction(dataResponse, payload, returnPayload)
          }
        }
      },
      timeout: 15000,
    })
  }

  return {
    ajaxSave,
    ajaxError,
  }
}
