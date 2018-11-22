<script>
export default {
  methods: {
    showErrorAlert (message, error, errorTitle) {
      $('#modalAlert').modal()
      if (errorTitle === null) {
        $('#modalAlert').find('.modal-header').text('Save Failed')
      } else {
        $('#modalAlert').find('.modal-header').text(`Save Failed due to ${errorTitle}`)
      }
      $('#modalAlert').find('.modal-header').addClass('text-danger')
      $('#modalAlert').find('.modal-body').text(`Failed to save a change to ${message} because ${error}. You should
          now refresh this page to ensure the data is up to date and then retry
          the action. If the problem persists please get in touch with
          the developers.`)
    },
  },
}
</script>
