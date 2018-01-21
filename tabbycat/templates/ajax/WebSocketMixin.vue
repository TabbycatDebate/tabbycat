<script>
// Subclass should set following methods
// - a data/prop of "tournamentId" that provides a tournament ID to be used
// - a data/prop of "socketPath" that provides a path like "/actionlog/latest"
//    - note the lack of trailing backslash in the above
// - handleSocketMessage() method that does something with the event data

export default {
  created: function() {
    var path = "/" + this.tournamentId + this.socketPath + "/"
    console.log("WS Connection", "wss://" + window.location.host + path)
    var sock = new WebSocket("wss://" + window.location.host + path)

    sock.onmessage = function(event) {
      var message = JSON.parse(event.data)
      this.handleSocketMessage(message.stream, message.payload)
    }.bind(this)
  }
}
</script>
