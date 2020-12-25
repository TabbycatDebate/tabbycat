import Vue from 'vue'
import Vuex from 'vuex'
import { splitDebates, sortInterleaved } from './DragAndDropShardingMethods.js'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

// The Vuex data store that contains the list of debates that are mutated
// and updated through websockets
export default new Vuex.Store({
  state: {
    debatesOrPanels: {}, // Keyed by primary key
    allocatableItems: {}, // Keyed by primary key
    extra: {},
    highlights: {},
    institutions: {},
    regions: {},
    loading: false, // Used by modal windows when waiting for an allocation etc
    round: null,
    tournament: null,
    // For saving mechanisms
    wsBridge: null,
    wsPseudoComponentID: null,
    lastSaved: null,
    // For hover panels
    hoverSubject: null,
    hoverType: null,
    // For hover conflicts
    hoverClashes: null,
    hoverHistories: null,
    // For sharding
    sharding: {
      split: null,
      mix: null,
      sort: null,
      index: null,
    },
  },
  mutations: {
    setupInitialData (state, initialData) {
      // Set primary data across all drag and drop views
      let loadDirectFromKey = ['round', 'tournament', 'extra']
      loadDirectFromKey.forEach((key) => {
        state[key] = initialData[key]
      })
      let LoadKeyedAsDictionary = ['debatesOrPanels', 'institutions', 'allocatableItems']
      LoadKeyedAsDictionary.forEach((key) => {
        initialData[key].forEach((item) => {
          state[key][item.id] = item // Load array in as id-key dictionary
        })
      })
      // Set Highlights
      Object.entries(initialData.extra.highlights).forEach(([key, value]) => {
        Vue.set(state.highlights, key, { active: false, options: {} })
        value.forEach((item, index) => {
          item.css = key + '-' + index
          state.highlights[key].options[item.pk] = item
        })
      })
      // Set Initial Sorting Order - using room rank for consistency with draw and preformed panels
      this.commit('setSorting', 'room_rank')
    },
    setupWebsocketBridge (state, bridge) {
      state.wsBridge = bridge // Load websocket into store for universal access
      state.wsPseudoComponentID = Math.floor(Math.random() * 10000)
    },
    setDebateOrPanelAttributes (state, changes) {
      // For a given set of debates or panels update their attribute values
      changes.forEach((debateOrPanel) => {
        if (state.debatesOrPanels[debateOrPanel.id]) {
          Object.entries(debateOrPanel).forEach(([key, value]) => {
            if (key !== 'id') {
              state.debatesOrPanels[debateOrPanel.id][key] = value
            }
          })
        } else {
          // We can receive entirely new debates; i.e. from create panels or
          // if the draw is edited and then an allocation runs
          Vue.set(state.debatesOrPanels, debateOrPanel.id, debateOrPanel)
        }
      })
    },
    setAllocatableAttributes (state, changes) {
      changes.forEach((allocatableItem) => {
        if (state.allocatableItems[allocatableItem.id]) {
          Object.entries(allocatableItem).forEach(([key, value]) => {
            if (key !== 'id') {
              state.allocatableItems[allocatableItem.id][key] = value
            }
          })
        }
      })
    },
    toggleHighlight (state, type) {
      Object.entries(state.highlights).forEach(([key, value]) => {
        if (key !== type) {
          value.active = false
        }
      })
      state.highlights[type].active = !state.highlights[type].active
    },
    setSorting (state, sortType) {
      let debatesArray = Object.values(state.debatesOrPanels)

      if (debatesArray.length === 0) {
        return // e.g. Preformed Panels page prior to use
      }

      let bracketKey = 'bracket_min' in debatesArray[0] ? 'bracket_min' : 'bracket'
      // Sort the array of debates according to specified sort type
      if (sortType === 'bracket') {
        if (debatesArray.length > 0 && bracketKey === 'bracket_min') {
          debatesArray.sort((a, b) => ((a.bracket_min + a.bracket_max) / 2) - ((b.bracket_min + b.bracket_max) / 2)).reverse()
        } else {
          debatesArray.sort((a, b) => a.bracket - b.bracket).reverse()
        }
      } else if (sortType === 'room_rank') {
        debatesArray.sort((a, b) => a.room_rank - b.room_rank)
      } else if (sortType === 'importance') {
        debatesArray.sort((a, b) =>
          a.importance - b.importance !== 0 ? a.importance - b.importance : a[bracketKey] - b[bracketKey]
        ).reverse() // Note: secondary sorting by bracket
      } else if (sortType === 'liveness') {
        // Same logic as in Drag and Drop Debate; should ideally be abstracted
        for (let debate of debatesArray) {
          if ('liveness' in debate === false) {
            debate.liveness = 0
            if ('teams' in debate && debate.teams) {
              for (const keyAndEntry of Object.entries(debate.teams)) {
                let team = keyAndEntry[1]
                // Team can be a number (ID) or null (e.g. when editing sides)
                if (team !== null && typeof team === 'object' && 'break_categories' in team) {
                  for (let bc of team.break_categories) {
                    let category = state.highlights.break.options[bc]
                    if (category && team.points > category.fields.dead && team.points < category.fields.safe) {
                      debate.liveness += 1
                    }
                  }
                }
              }
            }
          }
        }
        debatesArray.sort((a, b) =>
          a.liveness - b.liveness !== 0 ? a.liveness - b.liveness : a[bracketKey] - b[bracketKey]
        ).reverse() // Note: secondary sorting by bracket
      }
      // Using the sorted array, assign an index to the original dictionary values to be used by sortedDebatesOrPanels()
      for (let i = 0; i < debatesArray.length; i++) {
        state.debatesOrPanels[debatesArray[i].id]['sort_index'] = i
      }
    },
    setSharding (state, payload) {
      state.sharding[payload.option] = payload.value
    },
    setHoverPanel (state, payload) {
      state.hoverSubject = payload.subject
      state.hoverType = payload.type
    },
    unsetHoverPanel (state) {
      state.hoverSubject = null
      state.hoverType = null
    },
    setHoverConflicts (state, payload) {
      state.hoverClashes = payload.clashes
      state.hoverHistories = payload.histories
    },
    unsetHoverConflicts (state) {
      state.hoverClashes = null
      state.hoverHistories = null
    },
    updateSaveCounter (state) {
      state.lastSaved = new Date()
    },
    setLoadingState (state, isLoading) {
      state.loading = isLoading
    },
  },
  getters: {
    allDebatesOrPanels: state => {
      return state.debatesOrPanels
    },
    allInstitutions: state => {
      return state.institutions
    },
    allAdjudicators: state => {
      return state.allocatableItems
    },
    allTeams: state => {
      let teams = {}
      for (let debateOrPanelID in state.debatesOrPanels) {
        let debateOrPanel = state.debatesOrPanels[debateOrPanelID]
        if ('teams' in debateOrPanel) {
          for (let position in debateOrPanel.teams) {
            if (debateOrPanel.teams[position] !== null) {
              teams[debateOrPanel.teams[position].id] = debateOrPanel.teams[position]
            }
          }
        }
      }
      return teams
    },
    shardedDebatesOrPanels: state => {
      let debatesArray = Object.values(state.debatesOrPanels)
      if (state.sharding.index === null || debatesArray.length === 0) {
        return debatesArray
      }
      // Order debates
      let sortKey = 'bracket' // Default
      if (state.sharding.sort === 'Bracket') {
        sortKey = 'bracket_min' in debatesArray[0] ? 'bracket_min' : 'bracket'
      } else if (state.sharding.sort === 'Importance') {
        sortKey = 'importance'
      }
      debatesArray.sort((a, b) => a[sortKey] - b[sortKey]).reverse()

      // Re-order them to be evenly distributed single array if interleaved
      if (state.sharding.mix === 'Interleaved') {
        debatesArray = sortInterleaved(debatesArray, state.sharding.split)
      }
      // Split up into sub arrays based on nominated shard size / index
      const shardedDebates = splitDebates(debatesArray, state.sharding.split)
      return shardedDebates[state.sharding.index]
    },
    sortedDebatesOrPanels: (state, getters) => {
      // sort_index here is assigned in setSorting()
      return getters.shardedDebatesOrPanels.sort((a, b) => a.sort_index - b.sort_index)
    },
    allocatableItems: state => {
      return state.allocatableItems
    },
    loadingState: state => {
      return state.loading
    },
    teamClashesForItem: (state) => (id) => {
      if ('clashes' in state.extra && 'teams' in state.extra.clashes) {
        return state.extra.clashes.teams[id]
      }
      return false
    },
    adjudicatorClashesForItem: (state) => (id) => {
      if ('clashes' in state.extra && 'teams' in state.extra.clashes) {
        return state.extra.clashes.adjudicators[id]
      }
      return false
    },
    teamHistoriesForItem: (state) => (id) => {
      if ('clashes' in state.extra && 'teams' in state.extra.clashes) {
        return state.extra.histories.teams[id]
      }
      return false
    },
    adjudicatorHistoriesForItem: (state) => (id) => {
      if ('clashes' in state.extra && 'teams' in state.extra.clashes) {
        return state.extra.histories.adjudicators[id]
      }
      return false
    },
    currentHoverClashes: (state) => {
      return state.hoverClashes
    },
    currentHoverHistories: (state) => {
      return state.hoverHistories
    },
    duplicateAdjudicatorAllocations: (state) => {
      let allocatedIDs = []
      let doubleAllocatedIDs = []
      for (let debateOrPanelID in state.debatesOrPanels) {
        const debate = state.debatesOrPanels[debateOrPanelID]
        for (let position in debate.adjudicators) {
          for (let adjudicatorID of debate.adjudicators[position]) {
            if (allocatedIDs.includes(adjudicatorID)) {
              doubleAllocatedIDs.push(adjudicatorID)
            } else {
              allocatedIDs.push(adjudicatorID)
            }
          }
        }
      }
      return doubleAllocatedIDs
    },
  },
  // Note actions are async
  actions: {
    updateDebatesOrPanelsAttribute ({ commit }, updatedDebatesOrPanels) {
      // Mutate debate/panel state to reflect the sent attributes via data like:
      // { attributeKey: [{ id: debateID, attributeKey: attributeValue ], ... }
      Object.entries(updatedDebatesOrPanels).forEach(([attribute, changes]) => {
        commit('setDebateOrPanelAttributes', changes)
      })
      // Send the result over the websocket, like:
      // "importance": [{ "id": 71, "importance": "0"} ], "componentID": 1407 }
      updatedDebatesOrPanels['componentID'] = this.state.wsPseudoComponentID
      this.state.wsBridge.send(updatedDebatesOrPanels)
      commit('updateSaveCounter')
      // TODO: error handling; locking; checking if the result matches sent data
    },
    updateAllocableItemModified ({ commit }, unallocatedItemIDs) {
      // To preserve the 'drag order' on the unallocated item we need to set the
      // modified attribute to be the current date time
      var changes = []
      const now = Math.round((new Date()).getTime() / 1000) // Unix time
      unallocatedItemIDs.forEach((id) => {
        changes.push({ 'id': id, 'vue_last_modified': now })
      })
      commit('setAllocatableAttributes', changes)
    },
    receiveUpdatedupdateDebatesOrPanelsAttribute ({ commit }, payload) {
      // Commit changes from websockets i.e.
      // { "componentID": 5711, "debatesOrPanels": [{ "id": 72, "importance": "0" }] }
      if ('message' in payload) {
        $.fn.showAlert(payload.message.type, payload.message.text, 0)
        commit('setLoadingState', false) // Hide and re-enable modals
      }
      // Don't update the data if it came from this store as it's mutated
      if (payload.componentID !== this.state.wsPseudoComponentID) {
        if (payload.debatesOrPanels) {
          commit('setDebateOrPanelAttributes', payload.debatesOrPanels)
        }
      }
    },
  },
  strict: debug,
})
