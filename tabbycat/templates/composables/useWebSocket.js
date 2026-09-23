// WebSocketBridge implementation for modern browsers
class WebSocketBridge {
  constructor() {
    this.socket = null
    this.listeners = {}
  }

  connect(url, protocols = [], options = {}) {
    this.socket = new WebSocket(url, protocols)

    this.socket.onopen = () => {
      this.emit('connected')
    }

    this.socket.onmessage = (event) => {
      this.emit('message', event)
    }

    this.socket.onclose = () => {
      this.emit('disconnected')
    }

    this.socket.onerror = (error) => {
      this.emit('error', error)
    }

    // Add reconnection logic if options provided
    if (options.reconnect !== false) {
      this.setupReconnection(url, protocols, options)
    }
  }

  setupReconnection(url, protocols, options) {
    const minDelay = options.minReconnectionDelay || 1000
    const maxDelay = options.maxReconnectionDelay || 30000
    const delayFactor = options.reconnectionDelayGrowFactor || 1.5
    let currentDelay = minDelay

    this.socket.onclose = () => {
      this.emit('disconnected')

      setTimeout(() => {
        if (this.socket.readyState === WebSocket.CLOSED) {
          this.connect(url, protocols, options)
          currentDelay = Math.min(currentDelay * delayFactor, maxDelay)
        }
      }, currentDelay)
    }
  }

  addEventListener(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }

  removeEventListener(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback)
    }
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data))
    }
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data))
    }
  }

  close() {
    if (this.socket) {
      this.socket.close()
    }
  }
}
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useModalError } from './useModalError.js'

export function useWebSocket (options) {
  const {
    sockets,
    tournamentSlugForWSPath,
    roundSlugForWSPath,
    getPathAdditions,
    handleSocketReceive,
    handleSocketError,
  } = options

  const bridges = reactive({})
  const lostConnections = ref(0)
  const componentId = Math.floor(Math.random() * 10000)

  const { showErrorAlert } = useModalError()

  const resolveMaybeRef = (val) => {
    if (val && typeof val === 'object' && 'value' in val) {
      return val.value
    }
    return val
  }

  const defaultGetPathAdditions = (path, socketLabel) => {
    let p = path
    const tournamentSlug = resolveMaybeRef(tournamentSlugForWSPath)
    const roundSlug = resolveMaybeRef(roundSlugForWSPath)

    if (tournamentSlug !== undefined) {
      p += `${tournamentSlug}/`
    }
    if (roundSlug !== undefined) {
      p += `round/${roundSlug}/`
    }
    p = `${p + socketLabel}/`
    return p
  }

  const logConnectionInfo = (statusType, socketPath) => {
    const now = new Date()
    const paddedMinutes = now.getMinutes() < 10 ? '0' + now.getMinutes() : now.getMinutes()
    const msg = `${now.getHours()}:${paddedMinutes} ${statusType} path:\n${socketPath}`
    console.debug(`${msg}\n(${lostConnections.value} prior loses)`)
  }

  const showLostConnectionAlert = () => {
    if (lostConnections.value > 1) {
      const explanation = `This page maintains a live connection to the server. That connection has
                           been lost. This page will attempt to reconnect and will update this message
                           if it succeeds. You can dismiss this warning if needed, just be aware that
                           you should not change data on this page until the connection resumes.`
      showErrorAlert(explanation, null, 'Connection Lost', 'text-danger', true, true)
    }
  }

  const dismissLostConnectionAlert = () => {
    if (lostConnections.value > 1) {
      const explanation = `This page lost its connection to the server but has successfully reopened
                           it. Changes made to data on this page will now be saved. However, you may
                           want to refresh the page to verify that earlier changes were saved.`
      showErrorAlert(explanation, null, 'Connection Resumed', 'text-success', true, true)
    }
  }

  const receiveFromSocket = (socketLabel, payload) => {
    let parsed = payload
    if (typeof payload === 'string') {
      try {
        parsed = JSON.parse(payload)
      } catch {
        parsed = payload
      }
    }

    if (parsed && Object.prototype.hasOwnProperty.call(parsed, 'error')) {
      if (parsed.component_id === componentId) {
        if (typeof handleSocketError === 'function') {
          handleSocketError(socketLabel, parsed)
        } else {
          showErrorAlert(parsed.error, parsed.message, null)
        }
      }
    } else {
      handleSocketReceive(socketLabel, parsed)
    }
  }

  const sendToSocket = (socketLabel, payload) => {
    const bridge = bridges[socketLabel]
    if (!bridge) {
      return
    }
    payload.component_id = componentId
    bridge.send(payload)
  }

  onMounted(() => {
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const basePath = `${scheme}://${window.location.host}/ws/`

    for (const socketLabel of sockets) {
      const socketPath = (getPathAdditions || defaultGetPathAdditions)(basePath, socketLabel)
      const webSocketBridge = new WebSocketBridge()
      webSocketBridge.connect(socketPath, undefined, {
        minReconnectionDelay: 5 * 1000,
        maxReconnectionDelay: 240 * 1000,
        reconnectionDelayGrowFactor: 1.5,
        connectionTimeout: 10 * 1000,
      })

      webSocketBridge.addEventListener('message', (payload) => {
        receiveFromSocket(socketLabel, payload.data)
      })

      webSocketBridge.socket.addEventListener('open', (() => {
        logConnectionInfo('connected to', socketPath)
        dismissLostConnectionAlert()
      }).bind(socketPath))

      webSocketBridge.socket.addEventListener('error', (() => {
        logConnectionInfo('error in', socketPath)
      }).bind(socketPath))

      webSocketBridge.socket.addEventListener('close', (() => {
        lostConnections.value += 1
        logConnectionInfo('disconnected from', socketPath)
        showLostConnectionAlert()
      }).bind(socketPath))

      bridges[socketLabel] = webSocketBridge
    }
  })

  onBeforeUnmount(() => {
    for (const [label, bridge] of Object.entries(bridges)) {
      try {
        bridge?.socket?.close()
      } catch (e) {
        // noop
      }
      delete bridges[label]
    }
  })

  return {
    bridges,
    lostConnections,
    componentId,
    sendToSocket,
  }
}
