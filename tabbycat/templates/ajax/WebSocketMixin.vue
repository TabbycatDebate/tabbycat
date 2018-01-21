<script>
// Subclass should set following methods
// - a data/prop of "tournamentId" that provides a tournament ID to be used
// - a data/prop of "socketPath" that provides a path like "/actionlog/latest"
//    - note the lack of trailing backslash in the above
// - handleSocketMessage() method that does something with the event data

export default {
  created: function() {
    // Check if this is being run over HTTP(S); match the WS(S) procol
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const path = "/" + this.tournamentId + this.socketPath + "/"

    // Open the connectoin
    console.log("WSConnect", scheme + "://" + window.location.host + path)
    var sock = new WebSocket(scheme + "://" + window.location.host + path)

    // Handle messages from the server
    sock.onmessage = function(event) {
      var message = JSON.parse(event.data)
      this.handleSocketMessage(message.stream, message.payload)
    }.bind(this)
  }
}
</script>
