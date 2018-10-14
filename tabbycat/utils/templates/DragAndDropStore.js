import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

// The Vuex data store that contains the list of debates that are mutated
// and updated through websockets
export default new Vuex.Store({
  state: {
    debatesOrPanels: {}, // Keyed by primary key
    round: null,
    tournament: null,
    extra: {},
    highlights: {},
    // For saving mechanisms
    wsBridge: null,
    wsPseudoComponentID: null,
    lastSaved: null,
  },
  mutations: {
    setupInitialData (state, initialData) {
      // Primary data across all drag and drop views
      state.round = initialData.round[0]
      state.tournament = initialData.tournament[0]
      initialData.debatesOrPanels.forEach((debateOrPanel) => {
        state.debatesOrPanels[debateOrPanel.pk] = debateOrPanel
      })
      // Universal data but extended on a per view basis
      state.extra = initialData.extra
      // Highlights
      Object.entries(initialData.highlights).forEach(([key, value]) => {
        Vue.set(state.highlights, key, { active: false, options: {} })
        value.forEach((item, index) => {
          item.css = key + '-display ' + key + '-' + index
          state.highlights[key].options[item.pk] = item
        })
      })
    },
    setupWebsocketBridge (state, bridge) {
      state.wsBridge = bridge
      state.wsPseudoComponentID = Math.floor(Math.random() * 10000)
    },
    setDebateOrPanelAttributes (state, debateOrPanel) {
      // For a given debate or panel set its state to match the given attributes
      Object.entries(debateOrPanel.attrs).forEach(([key, value]) => {
        state.debatesOrPanels[debateOrPanel.pk]['fields'][key] = value
      })
    },
    toggleHighlight (state, type) {
      Object.entries(state.highlights).forEach(([key, value]) => {
        value.active = false
      })
      state.highlights[type].active = !state.highlights[type].active
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
      Object.entries(updatedDebatesOrPanels).forEach(([pk, attrs]) => {
        commit('setDebateOrPanelAttributes', { 'pk': pk, 'attrs': attrs })
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
        Object.entries(payload.debatesOrPanels).forEach(([pk, attrs]) => {
          commit('setDebateOrPanelAttributes', { 'pk': pk, 'attrs': attrs })
        })
      }
    },
  },
  strict: debug,
})
