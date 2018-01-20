<script>
// Subclass should set following methods
// a data of "socketPath" that provides a string like "/actionlog/latest/"
// handleSocketMessage() method that does something with the event data

export default {
  created: function() {
    var sock = new WebSocket("ws://" + window.location.host + this.socketPath);
    sock.onmessage = function(event) {
      var message = JSON.parse(event.data).payload
      this.handleSocketMessage(message)
    }.bind(this)
  }
}
</script>
