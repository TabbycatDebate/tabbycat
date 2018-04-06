<script>
export default {
  methods: {
    ajaxSave: function (url, payload, message, completeFunction, failFunction,
                        returnPayload, showErrorModal = true) {
      var self = this
      var dataPayload = JSON.stringify(payload)
      $.ajax({
        type: "POST",
        url: url,
        data: dataPayload,
        contentType: "application/json",
        dataType: "json",
        error: function (hxr, textStatus, errorThrown) {
          if (showErrorModal === true) {
            self.ajaxError(message, hxr.responseText, textStatus, errorThrown)
          }
          if (failFunction !== null) {
            failfunction (payload, returnPayload)
          }
        },
        success: function (data, textStatus, xhr) {
          if (JSON.parse(data)["status"] === 503) {
            // A straight up 503 response doesn't hit error function
            this.error('', '', "503 Service Unavailable")
          } else {
            self.$eventHub.$emit('update-saved-counter', this.updateLastSaved)
            console.debug("AJAX: Saved " + message)
            console.debug('DEBUG: JSON ajaxSave success data:', data)
            var dataResponse = JSON.parse(data)
            if (completeFunction !== null) {
              completefunction (dataResponse, payload, returnPayload)
            }
          }
        },
        timeout: 15000 // sets timeout to 15 seconds
      });
    },
    ajaxError: function (message, responseText, textStatus, errorThrown) {
      $('#modalAlert').modal();
      $('#modalAlert').find('.modal-header').text('Save Failed: ' + errorThrown)
      $('#modalAlert').find('.modal-header').addClass('text-danger')
      if (errorThrown === 'timeout') {
        $('#modalAlert').find('.modal-body').text(
          "Failed to save a change to " + message + " because the server did " +
          "not respond in time. This could be because your internet access " +
          "is slow/unreliable, or the server is under heavy load. Best to " +
          "refresh this page to ensure the data is up to date."
        )
      } else {
        var error = "of a server error" // Default error
        var response = JSON.parse(responseText)
        if (typeof(response.message) !== 'undefined') {
          error = response.message // Get error text from response if provided
        }
        $('#modalAlert').find('.modal-body').text(
          "Failed to save a change to " + message + " because " + error +
          ". You should now refresh this page to ensure " +
          "the data is up to date and then retry the action. If the problem " +
          "persists please get in touch with the developers."
        )
      }
    }
  }
}
</script>
