<script>
// Subclass should set following methods
// - Optional data/prop of "tournamentSlug" with a tournament slug for the path
// - Optional data/prop of "roundSeq" with a round sequence ID for the path
// - a data prop of "sockets" that for all the socket paths to monitor
// - a handleSocketReceive() function that will handle the different
// sockets' messages as appropriate

import { WebSocketBridge } from 'django-channels'
import _ from 'lodash'

import ModalErrorMixin from '../errors/ModalErrorMixin.vue'


export default {
  mixins: [ModalErrorMixin],
  props: ['tournamentSlug', 'roundSeq'],
  data: function () {
    return { bridges: {}, component_id: Math.floor(Math.random() * 10000) }
  },
  created: function () {

    // Check if this is being run over HTTP(S); match the WS(S) procol
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    var path = scheme + "://" + window.location.host + "/ws/"
    // Construct path
    if (this.tournamentSlug !== undefined) {
      path += this.tournamentSlug + "/"
    }

    const receiveFromSocket = this.receiveFromSocket
    var self = this;

    // Setup each websocket connection
    _.forEach(this.sockets, function (socketLabel) {

      // Customise path per-socket
      var socketPath = path + socketLabel + "/"
      if (this.roundSeq !== undefined) {
        socketPath += this.roundSeq + "/"
      }

      // Open the connection
      const webSocketBridge = new WebSocketBridge()

      webSocketBridge.connect(socketPath, undefined, {
        autoReconnectMS: 10000, // Wait 10s inbetween attempts
        stopReconnectingAfter: 21000, // Doesn't seem to work
      })

      // Listen for messages and pass to the defined handleSocketMessage()
      webSocketBridge.listen(function (payload) {
        receiveFromSocket(socketLabel, payload)
      }.bind(receiveFromSocket));

      // Logs
      webSocketBridge.socket.addEventListener('open', function () {
        console.debug("Connected to WebSocket path:", socketPath)
      }.bind(socketPath))
      webSocketBridge.socket.addEventListener('close', function () {
        console.debug("Disconnected to WebSocket path:", socketPath)
      }.bind(socketPath))

      // Set the data to contain the socket bridge so we can send to it
      self.$set(self.bridges, socketLabel, webSocketBridge)

    }.bind(receiveFromSocket))
  },
  methods: {
    // Passes to inheriting components; receives a payload from a socket
    receiveFromSocket: function(socketLabel, payload) {
      // console.log(`Received payload ${JSON.stringify(payload)} from socket ${socketLabel}`)
      if (payload.hasOwnProperty('error')) {
        if (payload['component_id'] === this.component_id) {
          this.showErrorAlert(payload.error, payload.message, null)
        }
      } else {
        this.handleSocketReceive(payload)
      }
    },
    // Called by inheriting components; sends a given payload to a socket
    sendToSocket: function (socketLabel, payload) {
      // console.log(`Sent payload ${JSON.stringify(payload)} to socket ${socketLabel}`)
      payload['component_id'] = this.component_id // Pass on originating Vue instance
      this.bridges[socketLabel].send(payload);
    },
  }
}
</script>
