<script>
// Subclass should set following methods
// - Optional data/prop of "tournamentSlug" with a tournament slug for the path
// - Optional data/prop of "roundSeq" with a round sequence ID for the path
// - a data/prop of "socketPath" that provides a path like "/actionlog/latest"
//    - note the lack of appending/prepending backslash in the above
// - handleSocketMessage() method that does something with the event data

import { WebSocketBridge } from 'django-channels'

export default {
  props: [ 'tournamentSlug', 'roundSeq'],
  created: function() {

    // Check if this is being run over HTTP(S); match the WS(S) procol
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    var path = "/"
    // Construct path
    if (this.tournamentSlug !== undefined) {
      path += this.tournamentSlug + "/"
    }
    path += this.socketPath + "/"
    if (this.roundSeq !== undefined) {
      path += this.roundSeq + "/"
    }

    // Open the connection
    const webSocketBridge = new WebSocketBridge()
    webSocketBridge.connect(path)
    webSocketBridge.socket.addEventListener('open', function() {
      console.log("Connected to WebSocket path")
    })
    webSocketBridge.socket.addEventListener('close', function() {
      console.log("Disconnected to WebSocket path")
    })

    // Handle downstream
    webSocketBridge.listen(function(action, stream) {
      console.log("heard event", action, stream)
      this.handleSocketMessage('actionlog', action) // Hardcode stream
    }.bind(this))

    // For handling multiplexing
    // webSocketBridge.demultiplex('actionlog', function(action, stream) {
    //   console.log(action, stream)
    // })

  }
}
</script>
