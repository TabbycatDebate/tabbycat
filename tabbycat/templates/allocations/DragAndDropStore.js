import { defineStore } from 'pinia'
import { splitDebates, sortInterleaved } from './DragAndDropShardingMethods.js'

export const useDragAndDropStore = defineStore('dragAndDrop', {
  state: () => ({
    debatesOrPanels: {}, // Keyed by primary key
    allocatableItems: {}, // Keyed by primary key
    extra: {},
    highlights: {},
    institutions: {},
    regions: {},
    loading: false, // Used by modal windows when waiting for an allocation etc
    draggingPanel: false, // Needed to switch UI affordances for whole-panel drops
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
    // For hover venues (Edit Rooms view)
    hoverVenueCategories: null,
    hoverVenueDebateId: null,
    hoverVenueConstraintSets: null,
    hoverVenueConstraintDebateId: null,
    // For sharding
    sharding: {
      split: null,
      mix: null,
      sort: null,
      index: null,
    },
  }),
  getters: {
    allDebatesOrPanels: (state) => state.debatesOrPanels,
    allInstitutions: (state) => state.institutions,
    allAdjudicators: (state) => state.allocatableItems,
    allTeams: (state) => {
      const teams = {}
      for (const debateOrPanelID in state.debatesOrPanels) {
        const debateOrPanel = state.debatesOrPanels[debateOrPanelID]
        if ('teams' in debateOrPanel) {
          for (const position in debateOrPanel.teams) {
            if (debateOrPanel.teams[position] !== null) {
              teams[debateOrPanel.teams[position].id] = debateOrPanel.teams[position]
            }
          }
        }
      }
      return teams
    },
    shardedDebatesOrPanels: (state) => {
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
    sortedDebatesOrPanels () {
      // sort_index here is assigned in setSorting()
      return [...this.shardedDebatesOrPanels].sort((a, b) => a.sort_index - b.sort_index)
    },
    loadingState: (state) => state.loading,
    teamClashesForItem: (state) => (id) => state.extra.clashes?.teams?.[id] ?? false,
    adjudicatorClashesForItem: (state) => (id) => state.extra.clashes?.adjudicators?.[id] ?? false,
    panelClashesOrHistoriesForItem: (state) => (id, type) => {
      const panelAdjs = state.debatesOrPanels[id].adjudicators
      const panelAdjIds = Object.values(panelAdjs).map(position => position).flat()

      const clashesOrHistoriesCombined = { adjudicator: [], team: [], institution: [] }
      panelAdjIds.forEach((adjId) => {
        const clashesForAdj = state.extra[type].adjudicators[adjId] ?? { adjudicator: [], team: [], institution: [] }
        for (const [key, value] of Object.entries(clashesForAdj)) {
          clashesOrHistoriesCombined[key].push(...value)
        }
      })

      return clashesOrHistoriesCombined
    },
    teamHistoriesForItem: (state) => (id) => state.extra.histories?.teams?.[id] ?? false,
    adjudicatorHistoriesForItem: (state) => (id) => state.extra.histories?.adjudicators?.[id] ?? false,
    currentHoverClashes: (state) => state.hoverClashes,
    currentHoverHistories: (state) => state.hoverHistories,
    currentHoverVenueCategories: (state) => state.hoverVenueCategories,
    currentHoverVenueDebateId: (state) => state.hoverVenueDebateId,
    currentHoverVenueConstraintSets: (state) => state.hoverVenueConstraintSets,
    currentHoverVenueConstraintDebateId: (state) => state.hoverVenueConstraintDebateId,
    duplicateAdjudicatorAllocations: (state) => {
      const allocatedIDs = []
      const doubleAllocatedIDs = []
      for (const debateOrPanelID in state.debatesOrPanels) {
        const debate = state.debatesOrPanels[debateOrPanelID]
        for (const position in debate.adjudicators) {
          for (const adjudicatorID of debate.adjudicators[position]) {
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
    panelIsDragging: (state) => state.draggingPanel,
  },
  actions: {
    setupInitialData(initialData) {
      // Set primary data across all drag and drop views
      const loadDirectFromKey = ['round', 'tournament', 'extra']
      loadDirectFromKey.forEach((key) => {
        this[key] = initialData[key]
      })
      const LoadKeyedAsDictionary = ['debatesOrPanels', 'institutions', 'allocatableItems']
      LoadKeyedAsDictionary.forEach((key) => {
        initialData[key].forEach((item) => {
          this[key][item.id] = item // Load array in as id-key dictionary
        })
      })
      // Set Highlights
      Object.entries(initialData.extra.highlights).forEach(([key, value]) => {
        this.highlights[key] = { active: false, options: {} }
        value.forEach((item, index) => {
          item.css = key + '-' + index
          this.highlights[key].options[item.pk] = item
        })
      })
      // Set Initial Sorting Order - using room rank for consistency with draw and preformed panels
      this.setSorting('room_rank')
    },
    setupWebsocketBridge(bridge) {
      this.wsBridge = bridge // Load websocket into store for universal access
      this.wsPseudoComponentID = Math.floor(Math.random() * 10000)
    },
    setDebateOrPanelAttributes(changes) {
      // For a given set of debates or panels update their attribute values
      changes.forEach((debateOrPanel) => {
        if (this.debatesOrPanels[debateOrPanel.id]) {
          Object.entries(debateOrPanel).forEach(([key, value]) => {
            if (key !== 'id') {
              this.debatesOrPanels[debateOrPanel.id][key] = value
            }
          })
        } else {
          // We can receive entirely new debates; i.e. from create panels or
          // if the draw is edited and then an allocation runs
          this.debatesOrPanels[debateOrPanel.id] = debateOrPanel
        }
      })
    },
    setAllocatableAttributes(changes) {
      changes.forEach((allocatableItem) => {
        if (this.allocatableItems[allocatableItem.id]) {
          Object.entries(allocatableItem).forEach(([key, value]) => {
            if (key !== 'id') {
              this.allocatableItems[allocatableItem.id][key] = value
            }
          })
        }
      })
    },
    toggleHighlight(type) {
      Object.entries(this.highlights).forEach(([key, value]) => {
        if (key !== type) {
          value.active = false
        }
      })
      this.highlights[type].active = !this.highlights[type].active
    },
    setSorting(sortType) {
      const debatesArray = Object.values(this.debatesOrPanels)
      if (debatesArray.length === 0) {
        return // e.g. Preformed Panels page prior to use
      }

      const bracketKey = 'bracket_min' in debatesArray[0] ? 'bracket_min' : 'bracket'
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
          a.importance - b.importance !== 0 ? a.importance - b.importance : a[bracketKey] - b[bracketKey],
        ).reverse() // Note: secondary sorting by bracket
      } else if (sortType === 'liveness') {
        // Same logic as in Drag and Drop Debate; should ideally be abstracted
        for (const debate of debatesArray) {
          if ('liveness' in debate === false) {
            debate.liveness = 0
            if ('teams' in debate && debate.teams) {
              for (const keyAndEntry of Object.entries(debate.teams)) {
                const team = keyAndEntry[1]
                // Team can be a number (ID) or null (e.g. when editing sides)
                if (team !== null && typeof team === 'object' && 'break_categories' in team) {
                  for (const bc of team.break_categories) {
                    const category = this.highlights.break.options[bc]
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
          a.liveness - b.liveness !== 0 ? a.liveness - b.liveness : a[bracketKey] - b[bracketKey],
        ).reverse() // Note: secondary sorting by bracket
      }
      // Using the sorted array, assign an index to the original dictionary values to be used by sortedDebatesOrPanels()
      for (let i = 0; i < debatesArray.length; i++) {
        this.debatesOrPanels[debatesArray[i].id]['sort_index'] = i
      }
    },
    setSharding(payload) {
      this.sharding[payload.option] = payload.value
    },
    setHoverPanel(payload) {
      this.hoverSubject = payload.subject
      this.hoverType = payload.type
    },
    unsetHoverPanel() {
      this.hoverSubject = null
      this.hoverType = null
    },
    setHoverConflicts(payload) {
      this.hoverClashes = payload.clashes
      this.hoverHistories = payload.histories
    },
    unsetHoverConflicts() {
      this.hoverClashes = null
      this.hoverHistories = null
    },
    setHoverVenueConstraints(payload) {
      this.hoverVenueConstraintSets = payload.allowedSets
      this.hoverVenueConstraintDebateId = payload.debateId ?? null
    },
    unsetHoverVenueConstraints() {
      this.hoverVenueConstraintSets = null
      this.hoverVenueConstraintDebateId = null
    },
    setHoverVenue(payload) {
      this.hoverVenueCategories = payload.categories
      this.hoverVenueDebateId = payload.debateId
    },
    unsetHoverVenue() {
      this.hoverVenueCategories = null
      this.hoverVenueDebateId = null
    },
    updateSaveCounter() {
      this.lastSaved = new Date()
    },
    setLoadingState(isLoading) {
      this.loading = isLoading
    },
    setPanelDraggingTracker(status) {
      this.draggingPanel = status
    },
    updateDebatesOrPanelsAttribute(updatedDebatesOrPanels) {
      // Mutate debate/panel state to reflect the sent attributes via data like:
      // { attributeKey: [{ id: debateID, attributeKey: attributeValue ], ... }
      Object.entries(updatedDebatesOrPanels).forEach(([, changes]) => {
        this.setDebateOrPanelAttributes(changes)
      })
      // Send the result over the websocket, like:
      // "importance": [{ "id": 71, "importance": "0"} ], "componentID": 1407 }
      updatedDebatesOrPanels['componentID'] = this.wsPseudoComponentID
      this.wsBridge.send(updatedDebatesOrPanels)
      this.updateSaveCounter()
      // TODO: error handling; locking; checking if the result matches sent data
    },
    updateAllocatableItemModified(unallocatedItemIDs) {
      // To preserve the 'drag order' on the unallocated item we need to set the
      // modified attribute to be the current date time
      const changes = []
      const now = Math.round((new Date()).getTime() / 1000) // Unix time
      unallocatedItemIDs.forEach((id) => {
        changes.push({ id: id, vue_last_modified: now })
      })
      this.setAllocatableAttributes(changes)
    },
    receiveUpdatedupdateDebatesOrPanelsAttribute(payload) {
      // Commit changes from websockets i.e.
      // { "componentID": 5711, "debatesOrPanels": [{ "id": 72, "importance": "0" }] }
      if ('message' in payload) {
        $.fn.showAlert(payload.message.type, payload.message.text, 0)
        this.setLoadingState(false) // Hide and re-enable modals
      }
      // Don't update the data if it came from this store as it's mutated
      if (payload.componentID !== this.wsPseudoComponentID) {
        if (payload.debatesOrPanels) {
          this.setDebateOrPanelAttributes(payload.debatesOrPanels)
        }
      }
    },
  },
})
