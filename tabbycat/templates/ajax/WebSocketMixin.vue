<script>
// Subclass should set following methods
// - Optional data/prop of "tournamentSlug" with a tournament slug for the path
// - Optional data/prop of "roundSeq" with a round sequence ID for the path
// - a data prop of "sockets" that for all the socket paths to monitor
// - a handleSocketMessage() function that will handle the different 
// sockets' messages as appropriate

import { WebSocketBridge } from 'django-channels'
import _ from 'lodash'

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

    const handleMessage = this.handleSocketMessage

    // Setup each websocket connection
    _.forEach(this.sockets, function(socketLabel) {

      // Customise path per-socket
      var socketPath = path + socketLabel + "/"
      if (this.roundSeq !== undefined) {
        socketPath += this.roundSeq + "/"
      }

      // Open the connection
      const webSocketBridge = new WebSocketBridge()
      webSocketBridge.connect(socketPath)

      // Listen for messages and pass to the defined handleSocketMessage()
      webSocketBridge.listen(function(payload) {
        handleMessage(payload, socketLabel)
      }.bind(handleMessage));

      // Logs
      // webSocketBridge.socket.addEventListener('open', function() {
      //   console.log("Connected to WebSocket path:", socketPath)
      // }.bind(socketPath))
      // webSocketBridge.socket.addEventListener('close', function() {
      //   console.log("Disconnected to WebSocket path:", socketPath)
      // }.bind(socketPath))

    }.bind(handleMessage))
  }
}
</script>
