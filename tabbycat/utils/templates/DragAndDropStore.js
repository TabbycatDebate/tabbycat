import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

// The Vuex data store that contains the list of debates that are mutated
// and updated through websockets
export default new Vuex.Store({
  state: {
    debatesOrPanels: null,
    roundInfo: null, // Globally accessible but constant
    wsBridge: null,
    wsPseudoComponentID: null,
    lastSaved: null,
  },
  mutations: {
    setupDebatesOrPanels (state, setupDebatesOrPanels) {
      state.debatesOrPanels = setupDebatesOrPanels
    },
    setupRoundInfo (state, roundInfo) {
      state.roundInfo = roundInfo
    },
    setupWebsocketBridge (state, bridge) {
      state.wsBridge = bridge
      state.wsPseudoComponentID = Math.floor(Math.random() * 10000)
    },
    setDebateOrPanelAttributes (state, debateOrPanel) {
      // For a given debate or panel set its state to match the given attributes
      Object.entries(debateOrPanel.attrs).forEach(([key, value]) => {
        state.debatesOrPanels[debateOrPanel.id][key] = value
      })
    },
    updateSaveCounter (state) {
      state.lastSaved = new Date()
    },
  },
  getters: {
    allDebatesOrPanels: state => {
      return state.debatesOrPanels
    },
  },
  // Note actions are async
  actions: {
    updateDebatesOrPanelsAttribute ({ commit }, updatedDebatesOrPanels) {
      // For each debate or panel mutate the state to reflect the new attributes
      Object.entries(updatedDebatesOrPanels).forEach(([id, attrs]) => {
        commit('setDebateOrPanelAttributes', { 'id': id, 'attrs': attrs })
      })
      // Send the result over the websocket
      this.state.wsBridge.send({
        debatesOrPanels: updatedDebatesOrPanels,
        componentID: this.state.wsPseudoComponentID,
      })
      commit('updateSaveCounter')
      // TODO: error handling; locking; checking if the result matches send
    },
    receiveUpdatedupdateDebatesOrPanelsAttribute ({ commit }, payload) {
      // Only commit changes from websockets initiated from other instances
      if (payload.componentID !== this.state.wsPseudoComponentID) {
        Object.entries(payload.debatesOrPanels).forEach(([id, attrs]) => {
          commit('setDebateOrPanelAttributes', { 'id': id, 'attrs': attrs })
        })
      }
    },
  },
  strict: debug,
})
