<script>
export default {
  methods: {
    ajaxSave: function (url, payload, message, completeFunction) {
      var self = this
      $.ajax({
        type: "POST",
        url: url,
        data: payload,
        error: function(XMLHttpRequest, textStatus, errorThrown) {
          self.ajaxError(message, textStatus, errorThrown)
        },
        success: function() {
          self.$eventHub.$emit('update-saved-counter', this.updateLastSaved)
          console.log("AJAX: Successful save change for " + message)
        },
        complete: function() {
          completeFunction()
        }
      });
    },
    ajaxError: function(resourceType, textStatus, errorThrown) {
      $('#modalAlert').modal();
      $('#modalAlert').find('.modal-header').text('Save Failed')
      $('#modalAlert').find('.modal-header').addClass('text-danger')
      $('#modalAlert').find('.modal-body').text(
        'Failed to save a change to a ' + resourceType +
        '. Try making the change again, or try refreshing the page.'
      )
      console.log("Status: " + textStatus);
      console.log("Error: " + errorThrown);
    }
  }
}
</script>
