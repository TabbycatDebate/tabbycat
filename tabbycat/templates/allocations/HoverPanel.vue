<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import HoverPanelGroup from './HoverPanelGroup.vue'
import { useDragAndDropStore } from './DragAndDropStore.js'
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

const store = useDragAndDropStore()
const { gettext } = useDjangoI18n()
const {
  hoverSubject,
  hoverType,
  highlights,
  extra,
  allTeams,
  allInstitutions,
  allAdjudicators,
} = storeToRefs(store)

const makeItem = (title, css, icon) => ({ title: title, css: css, icon: icon })

const makePersonItem = (participant) => {
  return makeItem(
    participant.name + ` (${participant.gender ? participant.gender : '?'})`,
    `gender-display gender-${participant.gender}`,
    'user',
  )
}

const makeInstitutionItem = (subject) => {
  const institutionDetails = []
  if (subject?.institution) {
    const institution = allInstitutions.value?.[subject.institution]
    if (institution?.region && highlights.value?.region) {
      const regionName = highlights.value.region.options[institution.region]?.fields?.name
      const name = institution.code + ` (${!regionName ? 'No Region' : regionName})`
      const css = 'region-display ' + highlights.value.region.options[institution.region].css
      institutionDetails.push(makeItem(name, css, false))
    } else if (institution) {
      const name = institution.code
      const css = 'btn-outline-secondary'
      institutionDetails.push(makeItem(name, css, false))
    }
  }
  return institutionDetails
}

const makeClashItems = (clashes) => {
  let adjudicators = null
  if ('adjudicator' in clashes) {
    adjudicators = []
    for (const clash of clashes.adjudicator) {
      const adj = allAdjudicators.value?.[clash.id]
      if (adj) {
        adjudicators.push(makeItem(adj.name, 'conflictable hover-adjudicator', ''))
      }
    }
  }
  let institutions = null
  if ('institution' in clashes) {
    institutions = []
    for (const clash of clashes.institution) {
      const inst = allInstitutions.value?.[clash.id]
      if (inst) {
        institutions.push(makeItem(inst.code, 'conflictable hover-institution', ''))
      }
    }
  }
  let teams = null
  if ('team' in clashes && allTeams.value) {
    teams = []
    for (const clash of clashes.team) {
      if (clash.id in allTeams.value) {
        teams.push(makeItem(allTeams.value[clash.id].short_name, 'conflictable hover-team', ''))
      }
    }
  }
  return [institutions, teams, adjudicators]
}

const makeHistoryItems = (histories) => {
  const formattedHistories = {}
  if ('adjudicator' in histories) {
    for (const history of histories.adjudicator) {
      if (!(history.ago in formattedHistories)) {
        const css = `conflictable conflicts-toolbar hover-histories-${history.ago}-ago`
        formattedHistories[history.ago] = [makeItem(`-${history.ago}R`, css, false)]
      }
      if (history.id in allAdjudicators.value) {
        const adjName = allAdjudicators.value[history.id].name.split(' ')[0]
        const css = `btn-xs-text btn-outline-info conflictable panel-histories-${history.ago}-ago`
        formattedHistories[history.ago].push(makeItem(adjName, css, false))
      }
    }
  }
  if ('team' in histories && Object.keys(allTeams.value ?? {}).length > 0) {
    for (const history of histories.team) {
      if (!(history.ago in formattedHistories)) {
        const css = `conflictable conflicts-toolbar hover-histories-${history.ago}-ago`
        formattedHistories[history.ago] = [makeItem(`-${history.ago}R`, css, false)]
      }
      if (history.id in allTeams.value) {
        const teamName = allTeams.value[history.id].short_name
        const css = `btn-xs-text btn-outline-info conflictable panel-histories-${history.ago}-ago`
        formattedHistories[history.ago].push(makeItem(teamName, css, false))
      }
    }
  }
  const historyItems = []
  const roundKeys = Object.keys(formattedHistories).sort()
  for (const roundKey of roundKeys) {
    historyItems.push(formattedHistories[roundKey])
  }
  return historyItems
}

const topleftteam = computed(() => {
  if (!hoverSubject.value) return []
  const teamDetails = []
  if (extra.value?.codeNames !== 'everywhere') {
    teamDetails.push(makeItem(hoverSubject.value.short_name, 'btn-outline-secondary', false))
  }
  if (extra.value?.codeNames !== 'off') {
    let codeName = hoverSubject.value.code_name
    if (codeName === '') {
      codeName = gettext('No code name set')
    }
    teamDetails.push(makeItem(codeName, 'btn-outline-secondary', false))
  }
  const speakerDetails = []
  if (typeof hoverSubject.value.speakers !== 'undefined') {
    for (const speaker of hoverSubject.value.speakers) {
      speakerDetails.push(makePersonItem(speaker))
    }
  }
  const institutionDetails = makeInstitutionItem(hoverSubject.value)
  return [teamDetails, speakerDetails, institutionDetails]
})

const toprightteam = computed(() => {
  if (!hoverSubject.value) return []
  const points = hoverSubject.value.points ? hoverSubject.value.points : 0
  const pointsDetails = [makeItem(`On ${points} Points`, 'btn-outline-secondary', false)]
  if (hoverSubject.value.break_categories.length === 0) {
    const item = makeItem('No Break Categories Set', 'btn-outline-secondary', false)
    pointsDetails.push(item)
  } else if (highlights.value?.break) {
    for (const bc of hoverSubject.value.break_categories) {
      const category = highlights.value.break.options[bc]
      if (category) {
        const breakCSS = 'break-display ' + category.css
        let status = '?'
        let info = ''
        if (hoverSubject.value.points >= category.fields.safe) {
          status = 'SAFE'
          info = `(>${category.fields.safe - 1})`
        } else if (hoverSubject.value.points <= category.fields.dead) {
          status = 'DEAD'
          info = `(<${category.fields.dead + 1})`
        } else if (hoverSubject.value.points > category.fields.dead && hoverSubject.value.points < category.fields.safe) {
          status = 'LIVE'
          info = `(>${category.fields.dead})`
        }
        const item = makeItem(`${status} for ${category.fields.name} ${info}`, breakCSS, false)
        pointsDetails.push(item)
      }
    }
  }
  return [pointsDetails]
})

const bottomleftteam = computed(() => {
  if (!hoverSubject.value) return null
  const clashes = store.teamClashesForItem(hoverSubject.value.id)
  if (clashes) {
    return makeClashItems(clashes)
  }
  return null
})

const bottomrightteam = computed(() => {
  if (!hoverSubject.value) return null
  const histories = store.teamHistoriesForItem(hoverSubject.value.id)
  if (histories) {
    return makeHistoryItems(histories)
  }
  return null
})

const topleftadjudicator = computed(() => {
  if (!hoverSubject.value) return []
  const adjDetails = [makePersonItem(hoverSubject.value)]
  const institutionDetails = makeInstitutionItem(hoverSubject.value)
  return [adjDetails, institutionDetails]
})

const toprightadjudicator = computed(() => {
  if (!hoverSubject.value) return []
  const rankCategories = Object.keys(highlights.value?.rank?.options ?? {})
  let relevantCategory = null
  for (const rankCategory of rankCategories) {
    if (hoverSubject.value.score >= highlights.value.rank.options[rankCategory].fields.cutoff) {
      relevantCategory = highlights.value.rank.options[rankCategory]
      break
    }
  }
  if (!relevantCategory) return [[]]
  const css = 'rank-display ' + relevantCategory.css
  const roundedScore = Number.parseFloat(hoverSubject.value.score).toFixed(1)
  const score = makeItem(`${roundedScore} Feedback Score`, css, false)
  const rank = makeItem(`${relevantCategory.fields.name} Relevant Rank`, css, false)
  return [[score, rank]]
})

const bottomleftadjudicator = computed(() => {
  if (!hoverSubject.value) return null
  const clashes = store.adjudicatorClashesForItem(hoverSubject.value.id)
  if (clashes) {
    return makeClashItems(clashes)
  }
  return null
})

const bottomrightadjudicator = computed(() => {
  if (!hoverSubject.value) return null
  const histories = store.adjudicatorHistoriesForItem(hoverSubject.value.id)
  if (histories) {
    return makeHistoryItems(histories)
  }
  return null
})

const topRow = computed(() => {
  if (!hoverType.value) return { left: [], right: [] }
  if (hoverType.value === 'team') {
    return { left: topleftteam.value, right: toprightteam.value }
  }
  if (hoverType.value === 'adjudicator') {
    return { left: topleftadjudicator.value, right: toprightadjudicator.value }
  }
  return { left: [], right: [] }
})

const bottomRow = computed(() => {
  if (!hoverType.value) return { left: [], right: [] }
  if (hoverType.value === 'team') {
    return { left: bottomleftteam.value, right: bottomrightteam.value }
  }
  if (hoverType.value === 'adjudicator') {
    return { left: bottomleftadjudicator.value, right: bottomrightadjudicator.value }
  }
  return { left: [], right: [] }
})

const subject = computed(() => hoverSubject.value)
const panelRows = computed(() => [topRow.value, bottomRow.value])
</script>

<template>
  <transition name="slide-over">
    <div
      v-if="subject"
      class="panel slideover-info"
    >
      <template v-if="panelRows">
        <div
          v-for="(row, idx) in panelRows"
          :key="idx"
          class="list-group-item flex-horizontal pl-2 flex-justify"
        >
          <div class="flex-align-start">
            <hover-panel-group :groups="row['left']" />
          </div>
          <div>
            <hover-panel-group :groups="row['right']" />
          </div>
        </div>
      </template>
    </div>
  </transition>
</template>
