<script>
// Subclass should set following methods
// - Optional data/prop of "tournamentId" with a tournament ID for the path
// - Optional data/prop of "roundSeq" with a round sequence ID for the path
// - a data/prop of "socketPath" that provides a path like "/actionlog/latest"
//    - note the lack of appending/prepending backslash in the above
// - handleSocketMessage() method that does something with the event data

export default {
  props: [ 'tournamentId', 'roundSeq'],
  created: function() {
    // Check if this is being run over HTTP(S); match the WS(S) procol
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    var path = "/"
    // Construct path
    if (this.tournamentId !== undefined) {
      path += this.tournamentId + "/"
    }
    path += this.socketPath + "/"
    if (this.roundSeq !== undefined) {
      path += this.roundSeq + "/"
    }
    // if (this.sessionKey !== undefined) {
    //   path += "?session_key=" + this.sessionKey
    // }

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
