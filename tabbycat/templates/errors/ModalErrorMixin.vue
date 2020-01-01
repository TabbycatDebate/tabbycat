<script>
export default {
  methods: {
    showErrorAlert (message, error, title,
      classOverride = false, titleOverride = false, messageOverride = false) {
      $('#modalAlert').modal()
      if (title === null) {
        $('#modalAlert').find('.modal-header').text('Save Failed')
      } else if (titleOverride) {
        $('#modalAlert').find('.modal-header').text(title)
      } else {
        $('#modalAlert').find('.modal-header').text(`Save Failed due to ${title}`)
      }
      if (classOverride) {
        $('#modalAlert').find('.modal-header').removeClass('text-danger')
        $('#modalAlert').find('.modal-header').addClass(classOverride)
      } else {
        $('#modalAlert').find('.modal-header').addClass('text-danger')
      }
      if (messageOverride) {
        $('#modalAlert').find('.modal-body').text(message)
      } else {
        $('#modalAlert').find('.modal-body').text(`Failed to save a change to ${message} because
          ${error}. You should now refresh this page to ensure the data is up to date and then
          retry the action. If the problem persists please get in touch with the developers.`)
      }
    },
  },
}
</script>
