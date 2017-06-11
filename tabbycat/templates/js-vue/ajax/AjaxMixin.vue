<script>
export default {
  methods: {
    ajaxSave: function (url, payload, message, completeFunction) {
      var self = this
      $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(payload),
        contentType: "application/json",
        dataType: "json",
        error: function(hxr, textStatus, errorThrown) {
          self.ajaxError(message, hxr.responseText, textStatus, errorThrown)
        },
        success: function(data, textStatus, xhr) {
          self.$eventHub.$emit('update-saved-counter', this.updateLastSaved)
          console.log("AJAX: Saved " + message)
          var dataResponse = JSON.parse(data)
          completeFunction(dataResponse)
        },
      });
    },
    ajaxError: function(resourceType, errorMessage, textStatus, errorThrown) {
      $('#modalAlert').modal();
      $('#modalAlert').find('.modal-header').text('Save Failed')
      $('#modalAlert').find('.modal-header').addClass('text-danger')
      $('#modalAlert').find('.modal-body').text(
        'Failed to save a change to a ' + resourceType + ' because "' +
        errorMessage + '." Try making the change again, or try ' +
        'refreshing the page.'
      )
      console.log("Status: " + textStatus);
      console.log("Error: " + errorThrown);
    }
  }
}
</script>
