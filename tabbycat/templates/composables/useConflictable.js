import { computed } from 'vue'
import { useDragAndDropStore } from '../allocations/DragAndDropStore.js'

export function useConflictableHelpers () {
  const store = useDragAndDropStore()

  const isInstitutionInPanel = (idToFind, debateAdjudicators, debateAdjudicatorToExclude) => {
    let found = false
    Object.keys(debateAdjudicators).forEach(adjudicatorPosition => {
      for (const adjudicatorId of debateAdjudicators[adjudicatorPosition]) {
        if (adjudicatorId === debateAdjudicatorToExclude) {
          continue
        }
        const adjsInstitutionalConflicts = store.adjudicatorClashesForItem(adjudicatorId)
        if (adjsInstitutionalConflicts && 'institution' in adjsInstitutionalConflicts) {
          for (const institutionalConflict of adjsInstitutionalConflicts.institution) {
            if (institutionalConflict.id === idToFind) {
              found = true
              break
            }
          }
        }
      }
    })
    return found
  }

  const isInstitutionInDebateTeams = (idToFind, debateTeams) => {
    let found = false
    Object.keys(debateTeams).forEach(debateTeamPosition => {
      const team = debateTeams[debateTeamPosition]
      if (team !== null) {
        const teamsConflicts = store.teamClashesForItem(team.id)
        if (typeof teamsConflicts !== 'undefined') {
          if ('institution' in teamsConflicts) {
            for (const institutionalConflict of teamsConflicts.institution) {
              if (institutionalConflict.id === idToFind) {
                found = true
                break
              }
            }
          }
        }
      }
    })
    return found
  }

  const isAdjudicatorInPanel = (idToFind, debateAdjudicators) => {
    let found = false
    Object.keys(debateAdjudicators).forEach(adjudicatorPosition => {
      for (const adjudicatorId of debateAdjudicators[adjudicatorPosition]) {
        if (adjudicatorId === idToFind) {
          found = true
          break
        }
      }
    })
    return found
  }

  const isTeamInDebateTeams = (idToFind, debateTeams) => {
    let found = false
    Object.keys(debateTeams).forEach(teamPosition => {
      if (debateTeams[teamPosition]?.id === idToFind) {
        found = true
      }
    })
    return found
  }

  return {
    isInstitutionInPanel,
    isInstitutionInDebateTeams,
    isAdjudicatorInPanel,
    isTeamInDebateTeams,
  }
}

export function useConflictsCSS ({ hasClashConflict, hasInstitutionalConflict, hasHistoryConflict }) {
  const conflictsCSS = computed(() => {
    if (hasClashConflict.value) {
      return 'conflictable panel-adjudicator'
    } else if (hasInstitutionalConflict.value) {
      return 'conflictable panel-institution'
    } else if (hasHistoryConflict.value) {
      return `conflictable panel-histories-${hasHistoryConflict.value}-ago`
    }
    return ''
  })

  return { conflictsCSS }
}

export function useConflictableTeam ({ debateId, team, clashableType, clashableID }) {
  const store = useDragAndDropStore()
  const { isAdjudicatorInPanel, isInstitutionInPanel } = useConflictableHelpers()

  const allDebatesOrPanels = computed(() => store.allDebatesOrPanels)

  const safeDebate = computed(() => {
    if (!debateId.value) {
      return null
    }
    return allDebatesOrPanels.value?.[debateId.value] ?? null
  })

  const hasClashConflict = computed(() => {
    if (!debateId.value || !allDebatesOrPanels.value?.[debateId.value]) {
      return false
    }
    const debateAdjudicators = allDebatesOrPanels.value[debateId.value].adjudicators
    const clashes = store.teamClashesForItem(team.value.id)
    if (clashes && 'adjudicator' in clashes) {
      for (const clash of clashes.adjudicator) {
        if (isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
          return true
        }
      }
    }
    return false
  })

  const hasInstitutionalConflict = computed(() => {
    if (!debateId.value || !allDebatesOrPanels.value?.[debateId.value]) {
      return false
    }
    const debateAdjudicators = allDebatesOrPanels.value[debateId.value].adjudicators
    const clashes = store.teamClashesForItem(team.value.id)
    if (clashes && 'institution' in clashes) {
      for (const clash of clashes.institution) {
        if (isInstitutionInPanel(clash.id, debateAdjudicators, null)) {
          return true
        }
      }
    }
    return false
  })

  const hasHistoryConflict = computed(() => {
    if (!debateId.value || !allDebatesOrPanels.value?.[debateId.value]) {
      return false
    }
    const debateAdjudicators = allDebatesOrPanels.value[debateId.value].adjudicators
    const histories = store.teamHistoriesForItem(team.value.id)
    let smallestAgo = 99
    if (histories && 'adjudicator' in histories) {
      for (const clash of histories.adjudicator) {
        if (isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
          if (clash.ago < smallestAgo) {
            smallestAgo = clash.ago
          }
        }
      }
    }
    if (smallestAgo === 99) {
      return false
    }
    return smallestAgo
  })

  const maxOccurrences = computed(() => {
    if (store.currentHoverHistories && clashableType.value === 'team') {
      let hoverCount = 0
      if ('team' in store.currentHoverHistories) {
        for (const sourceHistory of store.currentHoverHistories.team) {
          if (sourceHistory.id === clashableID.value) {
            hoverCount += 1
          }
        }
      }
      if (hoverCount > 0) {
        return hoverCount
      }
    }

    if (!(debateId.value && team.value)) {
      return 0
    }

    const histories = store.teamHistoriesForItem(team.value.id)
    if (!histories || !('adjudicator' in histories)) {
      return 0
    }

    if (!safeDebate.value || !safeDebate.value.adjudicators) {
      return 0
    }

    const debateAdjudicators = safeDebate.value.adjudicators
    const counts = {}
    let maxCount = 0
    for (const history of histories.adjudicator) {
      if (isAdjudicatorInPanel(history.id, debateAdjudicators)) {
        counts[history.id] = (counts[history.id] || 0) + 1
        if (counts[history.id] > maxCount) {
          maxCount = counts[history.id]
        }
      }
    }
    return maxCount
  })

  return {
    hasClashConflict,
    hasInstitutionalConflict,
    hasHistoryConflict,
    maxOccurrences,
  }
}

export function useConflictableAdjudicator ({ debateOrPanelId, adjudicator, clashableType, clashableID }) {
  const store = useDragAndDropStore()
  const { isAdjudicatorInPanel, isInstitutionInPanel, isTeamInDebateTeams, isInstitutionInDebateTeams } = useConflictableHelpers()

  const allDebatesOrPanels = computed(() => store.allDebatesOrPanels)

  const safeDebateOrPanel = computed(() => {
    if (!debateOrPanelId.value) {
      return null
    }
    return allDebatesOrPanels.value?.[debateOrPanelId.value] ?? null
  })

  const hasPanelClashConflict = computed(() => {
    if (!safeDebateOrPanel.value || !safeDebateOrPanel.value.adjudicators) {
      return false
    }
    const debateAdjudicators = safeDebateOrPanel.value.adjudicators
    const clashes = store.adjudicatorClashesForItem(adjudicator.value.id)
    if (clashes && 'adjudicator' in clashes) {
      for (const clash of clashes.adjudicator) {
        if (isAdjudicatorInPanel(clash.id, debateAdjudicators)) {
          return true
        }
      }
    }
    return false
  })

  const hasTeamClashConflict = computed(() => {
    if (!safeDebateOrPanel.value || !('teams' in safeDebateOrPanel.value)) {
      return false
    }
    const debateTeams = safeDebateOrPanel.value.teams
    const clashes = store.adjudicatorClashesForItem(adjudicator.value.id)
    if (clashes && 'team' in clashes) {
      for (const clash of clashes.team) {
        if (isTeamInDebateTeams(clash.id, debateTeams)) {
          return true
        }
      }
    }
    return false
  })

  const hasPanelInstitutionalConflict = computed(() => {
    if (!safeDebateOrPanel.value || !safeDebateOrPanel.value.adjudicators) {
      return false
    }
    const debateAdjudicators = safeDebateOrPanel.value.adjudicators
    const clashes = store.adjudicatorClashesForItem(adjudicator.value.id)
    if (clashes && 'institution' in clashes) {
      for (const clash of clashes.institution) {
        if (isInstitutionInPanel(clash.id, debateAdjudicators, adjudicator.value.id)) {
          return true
        }
      }
    }
    return false
  })

  const hasTeamInstitutionalConflict = computed(() => {
    if (!safeDebateOrPanel.value || !('teams' in safeDebateOrPanel.value)) {
      return false
    }
    const debateTeams = safeDebateOrPanel.value.teams
    const clashes = store.adjudicatorClashesForItem(adjudicator.value.id)
    if (clashes && 'institution' in clashes) {
      for (const clash of clashes.institution) {
        if (isInstitutionInDebateTeams(clash.id, debateTeams)) {
          return true
        }
      }
    }
    return false
  })

  const hasPanelHistoryConflict = computed(() => {
    if (!safeDebateOrPanel.value || !safeDebateOrPanel.value.adjudicators) {
      return false
    }
    const debateAdjudicators = safeDebateOrPanel.value.adjudicators
    const histories = store.adjudicatorHistoriesForItem(adjudicator.value.id)
    let smallestAgo = 99
    if (histories && 'adjudicator' in histories) {
      for (const history of histories.adjudicator) {
        if (isAdjudicatorInPanel(history.id, debateAdjudicators)) {
          if (history.ago < smallestAgo) {
            smallestAgo = history.ago
          }
        }
      }
    }
    if (smallestAgo === 99) {
      return false
    }
    return smallestAgo
  })

  const hasTeamHistoryConflict = computed(() => {
    if (!safeDebateOrPanel.value || !('teams' in safeDebateOrPanel.value)) {
      return false
    }
    const debateTeams = safeDebateOrPanel.value.teams
    const histories = store.adjudicatorHistoriesForItem(adjudicator.value.id)
    let smallestAgo = 99
    if (histories && 'team' in histories) {
      for (const history of histories.team) {
        if (isTeamInDebateTeams(history.id, debateTeams)) {
          if (history.ago < smallestAgo) {
            smallestAgo = history.ago
          }
        }
      }
    }
    if (smallestAgo === 99) {
      return false
    }
    return smallestAgo
  })

  const hasClashConflict = computed(() => {
    if (debateOrPanelId.value && adjudicator.value) {
      if (hasPanelClashConflict.value) {
        return true
      } else if (hasTeamClashConflict.value) {
        return true
      }
    }
    return false
  })

  const hasInstitutionalConflict = computed(() => {
    if (debateOrPanelId.value && adjudicator.value) {
      if (hasPanelInstitutionalConflict.value) {
        return true
      } else if (hasTeamInstitutionalConflict.value) {
        return true
      }
    }
    return false
  })

  const hasHistoryConflict = computed(() => {
    if (debateOrPanelId.value && adjudicator.value) {
      if (hasPanelHistoryConflict.value) {
        return hasPanelHistoryConflict.value
      } else if (hasTeamHistoryConflict.value) {
        return hasTeamHistoryConflict.value
      }
    }
    return false
  })

  const maxOccurrences = computed(() => {
    if (store.currentHoverHistories && clashableType.value === 'adjudicator') {
      let hoverCount = 0
      if ('adjudicator' in store.currentHoverHistories) {
        for (const sourceHistory of store.currentHoverHistories.adjudicator) {
          if (sourceHistory.id === clashableID.value) {
            hoverCount += 1
          }
        }
      }
      if (hoverCount > 0) {
        return hoverCount
      }
    }

    if (!(debateOrPanelId.value && adjudicator.value)) {
      return 0
    }

    const histories = store.adjudicatorHistoriesForItem(adjudicator.value.id)
    if (!histories) {
      return 0
    }

    let adjMax = 0
    const debateOrPanel = safeDebateOrPanel.value
    if (debateOrPanel && 'adjudicator' in histories) {
      const debateAdjudicators = debateOrPanel.adjudicators
      const adjCounts = {}
      for (const history of histories.adjudicator) {
        if (isAdjudicatorInPanel(history.id, debateAdjudicators)) {
          adjCounts[history.id] = (adjCounts[history.id] || 0) + 1
          if (adjCounts[history.id] > adjMax) {
            adjMax = adjCounts[history.id]
          }
        }
      }
    }

    let teamMax = 0
    if (safeDebateOrPanel.value && 'teams' in safeDebateOrPanel.value && 'team' in histories) {
      const debateTeams = safeDebateOrPanel.value.teams
      const teamCounts = {}
      for (const history of histories.team) {
        if (isTeamInDebateTeams(history.id, debateTeams)) {
          teamCounts[history.id] = (teamCounts[history.id] || 0) + 1
          if (teamCounts[history.id] > teamMax) {
            teamMax = teamCounts[history.id]
          }
        }
      }
    }

    const max = Math.max(adjMax, teamMax)
    return max > 0 ? max : 0
  })

  return {
    hasClashConflict,
    hasInstitutionalConflict,
    hasHistoryConflict,
    maxOccurrences,
  }
}
