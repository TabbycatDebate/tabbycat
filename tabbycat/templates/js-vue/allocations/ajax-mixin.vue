<script>
var ajaxMixin = {
  methods: {
    update: function (url, data, resourceType) {
      $.ajax({
        type: "POST",
        url: url,
        data: data,
        error: function(XMLHttpRequest, textStatus, errorThrown) {
          $('#modalAlert').modal();
          $('#modalAlert').find('.modal-title').text('Save Failed')
          $('#modalAlert').find('.modal-body').text(
            'Failed to save a change to a ' + resourceType +
            ' Try making the change again, otherwise try refreshing the page.'
          )
          console.log("Status: " + textStatus);
          console.log("Error: " + errorThrown);
        }
      });
    }
  }
}
</script>