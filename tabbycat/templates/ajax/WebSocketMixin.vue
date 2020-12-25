<script>
// Subclass should set following methods
// - Optional computed property of "tournamentSlugForWSPath" with a tournament slug for the path
// - Optional computed property  of "roundSlugForWSPath" with a round sequence ID for the path
// - a data prop of "sockets" that for all the socket paths to monitor
// - a handleSocketReceive() function that will handle the different
// sockets' messages as appropriate

import { WebSocketBridge } from 'django-channels'
import ModalErrorMixin from '../errors/ModalErrorMixin.vue'

export default {
  mixins: [ModalErrorMixin],
  data: function () {
    return { bridges: {}, lostConnections: 0, componentId: Math.floor(Math.random() * 10000) }
  },
  created: function () {
    // Check if this is being run over HTTP(S); match the WS(S) procol
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const path = `${scheme}://${window.location.host}/ws/`
    // Construct path

    const receiveFromSocket = this.receiveFromSocket
    const self = this

    // Setup each websocket connection
    for (const socketLabel of this.sockets) {
      // Customise path per-socket
      const socketPath = self.getPathAdditions(path, socketLabel)

      // Open the connection
      const webSocketBridge = new WebSocketBridge()
      webSocketBridge.connect(socketPath, undefined, {
        minReconnectionDelay: 5 * 1000, // Wait 5s inbetween attempts
        maxReconnectionDelay: 240 * 1000, // Cap waits at 4m inbetween attempts
        reconnectionDelayGrowFactor: 1.5, // Wait extra 7.5s inbetween
        connectionTimeout: 10 * 1000,
      })

      // Listen for messages and pass to the defined handleSocketMessage()
      webSocketBridge.listen((payload) => {
        receiveFromSocket(socketLabel, payload)
      })

      // Logs
      webSocketBridge.socket.addEventListener('open', (() => {
        self.logConnectionInfo('connected to', socketPath)
        self.dismissLostConnectionAlert()
      }).bind(socketPath, self))
      webSocketBridge.socket.addEventListener('error', (() => {
        self.logConnectionInfo('error in', socketPath)
      }).bind(socketPath, self))
      webSocketBridge.socket.addEventListener('close', (() => {
        self.lostConnections += 1
        self.logConnectionInfo('disconnected from', socketPath)
        self.showLostConnectionAlert()
      }).bind(socketPath, self))

      // Set the data to contain the socket bridge so we can send to it
      self.$set(self.bridges, socketLabel, webSocketBridge)
    }
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
    logConnectionInfo: function (statusType, socketPath) {
      const now = new Date()
      const paddedMinutes = now.getMinutes() < 10 ? '0' + now.getMinutes() : now.getMinutes()
      const msg = `${now.getHours()}:${paddedMinutes} ${statusType} path:\n${socketPath}`
      console.debug(`${msg}\n(${this.lostConnections} prior loses)`)
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
    showLostConnectionAlert: function () {
      if (this.lostConnections > 1) {
        const explanation = `This page maintains a live connection to the server. That connection has
                           been lost. This page will attempt to reconnect and will update this message
                           if it succeeds. You can dismiss this warning if needed, just be aware that
                           you should not change data on this page until the connection resumes.`
        this.showErrorAlert(explanation, null, 'Connection Lost', 'text-danger', true, true)
      }
    },
    dismissLostConnectionAlert: function () {
      if (this.lostConnections > 1) { // Only show modal when a connection is re-opened not opened
        const explanation = `This page lost its connection to the server but has succesfully reopened
                           it. Changes made to data on this page will now be saved. However, you may
                           want to refresh the page to verify that earlier changes were saved.`
        this.showErrorAlert(explanation, null, 'Connection Resumed', 'text-success', true, true)
      }
    },
  },
}
</script>
