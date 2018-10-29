<script>
// Subclass should set following methods
// - Optional computed property of "tournamentSlugForWSPath" with a tournament slug for the path
// - Optional computed property  of "roundSlugForWSPath" with a round sequence ID for the path
// - a data prop of "sockets" that for all the socket paths to monitor
// - a handleSocketReceive() function that will handle the different
// sockets' messages as appropriate

import _ from 'lodash'
import { WebSocketBridge } from 'django-channels'

import ModalErrorMixin from '../errors/ModalErrorMixin.vue'

export default {
  mixins: [ModalErrorMixin],
  data: function () {
    return { bridges: {}, componentId: Math.floor(Math.random() * 10000) }
  },
  created: function () {
    // Check if this is being run over HTTP(S); match the WS(S) procol
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    let path = `${scheme}://${window.location.host}/ws/`
    // Construct path

    const receiveFromSocket = this.receiveFromSocket
    const self = this

    // Setup each websocket connection
    _.forEach(this.sockets, function (socketLabel) {
      // Customise path per-socket
      const socketPath = self.getPathAdditions(path, socketLabel)

      // Open the connection
      const webSocketBridge = new WebSocketBridge()
      webSocketBridge.connect(socketPath, undefined, {
        minReconnectionDelay: 5 * 1000, // Wait 5s inbetween attempts
        maxReconnectionDelay: 240 * 1000, // Cap waits at 4m inbetween attempts
        reconnectionDelayGrowFactor: 2, // Wait extra 10s inbetween
        connectionTimeout: 10 * 1000,
      })

      // Listen for messages and pass to the defined handleSocketMessage()
      webSocketBridge.listen((payload) => {
        receiveFromSocket(socketLabel, payload)
      })

      // Logs
      webSocketBridge.socket.addEventListener('open', (() => {
        console.debug('Connected to WebSocket path:', socketPath)
      }).bind(socketPath, self))
      webSocketBridge.socket.addEventListener('close', (() => {
        console.debug('Disconnected to WebSocket path:', socketPath)
      }).bind(socketPath, self))

      // Set the data to contain the socket bridge so we can send to it
      self.$set(self.bridges, socketLabel, webSocketBridge)
    })
  },
  methods: {
    getPathAdditions: function (path, socketLabel) {
      // Allows for manual overrides to provide full paths
      if (this.tournamentSlugForWSPath !== undefined) {
        path += `${this.tournamentSlugForWSPath}/`
      }
      if (this.roundSlugForWSPath !== undefined) {
        path += `round/${this.roundSlugForWSPath}/`
      }
      path = `${path + socketLabel}/`
      return path
    },
    // Passes to inheriting components; receives a payload from a socket
    receiveFromSocket: function (socketLabel, payload) {
      // console.log(`Received payload ${JSON.stringify(payload)} from socket ${socketLabel}`)
      if (Object.prototype.hasOwnProperty.call(payload, 'error')) {
        if (payload.component_id === this.componentId) {
          this.showErrorAlert(payload.error, payload.message, null)
        }
      } else {
        this.handleSocketReceive(socketLabel, payload)
      }
    },
    // Called by inheriting components; sends a given payload to a socket
    sendToSocket: function (socketLabel, payload) {
      // console.log(`Sent payload ${JSON.stringify(payload)} to socket ${socketLabel}`)
      payload.component_id = this.componentId // Pass on originating Vue instance
      this.bridges[socketLabel].send(payload)
    },
  },
}
</script>
