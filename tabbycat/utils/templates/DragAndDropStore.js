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
  },
  mutations: {
    setupDebatesOrPanels (state, setupDebatesOrPanels) {
      state.debatesOrPanels = setupDebatesOrPanels
    },
    setupRoundInfo (state, roundInfo) {
      state.roundInfo = roundInfo
    },
  },
  getters: {
    allDebatesOrPanels: state => {
      return state.debatesOrPanels
    },
  },
  strict: debug,
})
