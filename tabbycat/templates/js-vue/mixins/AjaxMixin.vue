<script>
export default {
  methods: {
    update: function (url, data, resourceType) {
      $.ajax({
        type: "POST",
        url: url,
        data: data,
        error: function(XMLHttpRequest, textStatus, errorThrown) {
          $('#modalAlert').modal();
          $('#modalAlert').find('.modal-header').text('Save Failed')
          $('#modalAlert').find('.modal-header').addClass('text-danger')
          $('#modalAlert').find('.modal-body').text(
            'Failed to save a change to a ' + resourceType +
            '. Try making the change again, or try refreshing the page.'
          )
          console.log("Status: " + textStatus);
          console.log("Error: " + errorThrown);
        },
        success: function() {
          console.log("Saved change for " + resourceType)
          // If an autosave counter exists; update it
          var savedAt = new Date()
          var hours = savedAt.getHours()
          var minutes = ('0'+ savedAt.getMinutes()).slice(-2); // ":09" not ":9"
          $('#saveTime').text("Saved at " + hours + ":" + minutes)
        }
      });
    }
  }
}
</script>
