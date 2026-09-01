<script setup>
import { computed } from 'vue'

const props = defineProps({
  breakCategory: Object,
  teamsInDebate: Number,
  breakingTeams: Array,
  rounds: Array,
  sideNames: Object,
})

const COL_WIDTH = 192
const CONNECTOR_W = 40
const SLOT_GAP = 16
const SLOT_HEIGHT = 30

const slotH = computed(() => props.teamsInDebate * SLOT_HEIGHT)

// --- Utilities ---

function nextPow2(n) {
  if (n <= 1) return 1
  return 1 << Math.ceil(Math.log2(n))
}

function isPow2(n) {
  return n > 0 && (n & (n - 1)) === 0
}

function partialBreakRoundSplit(breakSize) {
  const r2 = nextPow2(breakSize) >> 1
  const debates = breakSize - r2
  return { debates, bypassing: r2 - debates }
}

function visualOrder(n) {
  if (n <= 1) return [1]
  const h = n >> 1
  const parent = visualOrder(h)
  const out = []
  for (const j of parent) out.push(j, 2 * h + 1 - j)
  return out
}

function foldParent(childRank, parentCount) {
  if (childRank <= parentCount) return childRank
  return 2 * parentCount + 1 - childRank
}

// --- Team map ---

const teamById = computed(() => {
  const m = {}
  props.breakingTeams.forEach(bt => {
    m[bt.team.id] = { ...bt.team, breakRank: bt.break_rank }
  })
  return m
})

// --- Side labels ---

function sideLabel(side) {
  return props.sideNames[side] ?? ''
}

// --- Server data parsing ---

function parseServerSlots(round) {
  if (!round.pairings) return null
  return round.pairings.map(p => {
    const sidesConfirmed = p.sides_confirmed !== false
    let teams = p.teams.map(t => ({
      teamId: t.team_id,
      side: sidesConfirmed ? t.side : null,
      advancing: t.advancing,
      team: teamById.value[t.team_id] ?? null,
    }))
    if (!sidesConfirmed) {
      teams.sort((a, b) => (a.team?.breakRank ?? 999) - (b.team?.breakRank ?? 999))
    }
    return {
      roomRank: p.room_rank,
      resultStatus: p.result_status,
      sidesConfirmed,
      teams,
    }
  })
}

// --- Layout helpers ---

function sortAnchor(col, sh) {
  const n = col.slots.length
  const step = sh + SLOT_GAP
  if (isPow2(n) && n > 1) {
    const vo = visualOrder(n)
    const r2v = {}
    vo.forEach((r, i) => { r2v[r] = i })
    col.slots.sort((a, b) => (r2v[a.roomRank] ?? 0) - (r2v[b.roomRank] ?? 0))
  }
  col.slots.forEach((s, i) => { s.yCenter = i * step + sh / 2 })
}

function centerFromPrev(col, prevCol) {
  col.slots.forEach(slot => {
    const children = prevCol.slots.filter(s => s._parentRank === slot.roomRank)
    if (children.length) {
      slot.yCenter = children.reduce((sum, c) => sum + c.yCenter, 0) / children.length
    }
  })
  col.slots.sort((a, b) => a.yCenter - b.yCenter)
}

function positionPreAnchor(col, nextCol, sh) {
  const step = sh + SLOT_GAP
  const nextYMap = {}
  nextCol.slots.forEach(s => { nextYMap[s.roomRank] = s.yCenter })

  const groups = {}
  col.slots.forEach(s => {
    const t = s._parentRank
    if (!groups[t]) groups[t] = []
    groups[t].push(s)
  })

  for (const [rank, slots] of Object.entries(groups)) {
    const parentY = nextYMap[parseInt(rank)] ?? 0
    if (slots.length === 1) {
      slots[0].yCenter = parentY
    } else {
      const totalH = slots.length * sh + (slots.length - 1) * SLOT_GAP
      const startY = parentY - totalH / 2 + sh / 2
      slots.forEach((s, i) => { s.yCenter = startY + i * step })
    }
  }
  col.slots.sort((a, b) => a.yCenter - b.yCenter)
}

function assignParentRanks(cols, isPartial, isBP, breakSize) {
  const bpBypass = isBP ? Math.floor(breakSize / 3) : 0
  for (let c = 0; c < cols.length - 1; c++) {
    const nextN = cols[c + 1].slots.length
    for (const slot of cols[c].slots) {
      if (isPartial && c === 0 && isBP) {
        slot._parentRank = slot.roomRank - bpBypass
      } else {
        slot._parentRank = foldParent(slot.roomRank, nextN)
      }
    }
  }
}

function computeTotalHeight(cols, sh) {
  let maxBot = 0
  for (const col of cols) {
    for (const s of col.slots) {
      maxBot = Math.max(maxBot, s.yCenter + sh / 2)
    }
  }
  return maxBot + SLOT_GAP
}

function buildConnectors(cols) {
  const out = []
  for (let c = 0; c < cols.length - 1; c++) {
    const toMap = {}
    cols[c + 1].slots.forEach(s => { toMap[s.roomRank] = s })
    for (const slot of cols[c].slots) {
      const target = toMap[slot._parentRank]
      if (target) {
        out.push({
          fromY: slot.yCenter,
          toY: target.yCenter,
          colIndex: c,
          inferred: !!(slot.inferred || target.inferred),
        })
      }
    }
  }
  return out
}

function markSeeds(cols, bypassing) {
  const seen = new Set()
  for (const col of cols) {
    for (const slot of col.slots) {
      for (const t of slot.teams) {
        if (!t.team) continue
        if (slot.inferred || !seen.has(t.teamId)) {
          t.showSeed = t.team.breakRank
        }
        if (!slot.inferred) seen.add(t.teamId)
        if (bypassing > 0 && t.team.breakRank <= bypassing) {
          t.isSeeded = true
        }
      }
    }
  }
}

// --- Inference helpers (mirror Python fold logic) ---

function makeTeamObj(bt) {
  return {
    teamId: bt.team.id,
    side: null,
    advancing: null,
    team: teamById.value[bt.team.id] ?? null,
  }
}

function makeInferredSlot(roomRank, teams) {
  return {
    roomRank,
    sidesConfirmed: false,
    inferred: true,
    resultStatus: null,
    teams: teams.map(t => ({ teamId: t.teamId, side: null, advancing: null, team: t.team })),
  }
}

function fold2Way(teams, startRoomRank = 0) {
  const n = teams.length >> 1
  const top = teams.slice(0, n)
  const bottom = teams.slice(n).reverse()
  return top.map((t, i) => makeInferredSlot(startRoomRank + i + 1, [t, bottom[i]]))
}

function fold4Way(teams, startRoomRank = 0) {
  const n = teams.length >> 2
  const pools = [
    teams.slice(0, n),
    teams.slice(n, 2 * n).reverse(),
    teams.slice(2 * n, 3 * n),
    teams.slice(3 * n, 4 * n).reverse(),
  ]
  return Array.from({ length: n }, (_, i) =>
    makeInferredSlot(startRoomRank + i + 1, [pools[0][i], pools[1][i], pools[2][i], pools[3][i]]),
  )
}

function getAdvancingFromCol(col, isBP) {
  const sorted = [...col.slots].sort((a, b) => a.roomRank - b.roomRank)
  if (isBP) {
    const pairs = []
    for (const slot of sorted) {
      const adv = slot.teams.filter(t => t.advancing === true)
      if (adv.length < 2) return null
      pairs.push(adv)
    }
    return pairs
  }
  const winners = []
  for (const slot of sorted) {
    const w = slot.teams.find(t => t.advancing === true)
    if (!w) return null
    winners.push(w)
  }
  return winners
}

function inferMissingPairings(cols, breakSize, isPartial, isBP) {
  const btObjs = props.breakingTeams.map(makeTeamObj)
  const { bypassing } = partialBreakRoundSplit(breakSize)
  const bpBypass = isBP ? Math.floor(breakSize / 3) : 0

  for (let c = 0; c < cols.length; c++) {
    if (cols[c].slots.some(s => s.teams.length > 0)) continue

    let inferred = null

    if (c === 0) {
      if (isBP) {
        if (isPartial) {
          inferred = fold4Way(btObjs.slice(bpBypass), bpBypass)
        } else {
          inferred = fold4Way(btObjs)
        }
      } else {
        inferred = fold2Way(btObjs.slice(bypassing), bypassing)
      }
    } else {
      const adv = getAdvancingFromCol(cols[c - 1], isBP)

      if (isPartial && c === 1 && !isBP) {
        // After-partial 2-team: bypassing teams are always known;
        // winners may or may not be available yet.
        const bypTeams = btObjs.slice(0, bypassing)
        const tbd = { teamId: null, side: null, advancing: null, team: null }
        const winners = adv ?? cols[c - 1].slots.map(() => tbd)
        const combined = [...bypTeams, ...winners]
        inferred = fold2Way(combined)
      } else if (isPartial && c === 1 && isBP) {
        const byp = btObjs.slice(0, bpBypass)
        const nd = byp.length >> 1
        const bypTop = byp.slice(0, nd)
        const bypBot = byp.slice(nd).reverse()
        const tbd = { teamId: null, side: null, advancing: null, team: null }
        const advPairs = adv ?? cols[c - 1].slots.map(() => [tbd, tbd])
        inferred = bypTop.map((t, i) =>
          makeInferredSlot(i + 1, [t, bypBot[i], ...advPairs[i]]),
        )
      } else {
        if (!adv) continue

        if (isBP) {
          const n = adv.length >> 1
          const top = adv.slice(0, n)
          const bot = adv.slice(n).reverse()
          inferred = top.map((tp, i) =>
            makeInferredSlot(i + 1, [...tp, ...bot[i]]),
          )
        } else {
          inferred = fold2Way(adv)
        }
      }
    }

    if (inferred) cols[c].slots = inferred
  }
}

// --- Main bracket computation ---

const bracket = computed(() => {
  const bs = props.breakCategory.breakSize
  if (bs < 2 || !props.breakingTeams.length || !props.rounds.length) return null
  try {
    return props.teamsInDebate === 2 ? build2Team(bs) : buildBP(bs)
  } catch (e) {
    console.error('Bracket error:', e)
    return null
  }
})

function makePlaceholderSlots(count, startRank) {
  return Array.from({ length: Math.max(1, count) }, (_, i) => ({
    roomRank: startRank + i,
    teams: [],
    resultStatus: null,
  }))
}

function build2Team(breakSize) {
  const { debates: r1Count, bypassing } = partialBreakRoundSplit(breakSize)
  const partial = bypassing > 0
  const fullBase = nextPow2(breakSize) >> 1
  const sh = slotH.value

  const cols = props.rounds.map((sr, ri) => {
    let slots = parseServerSlots(sr)
    if (!slots) {
      if (partial && ri === 0) {
        slots = makePlaceholderSlots(r1Count, bypassing + 1)
      } else {
        const off = partial ? 1 : 0
        slots = makePlaceholderSlots(fullBase >> (ri - off), 1)
      }
    }
    slots.sort((a, b) => a.roomRank - b.roomRank)
    return { name: sr.name, slots }
  })

  inferMissingPairings(cols, breakSize, partial, false)

  const anchorIdx = partial ? Math.min(1, cols.length - 1) : 0
  assignParentRanks(cols, partial, false, breakSize)
  sortAnchor(cols[anchorIdx], sh)
  for (let c = anchorIdx + 1; c < cols.length; c++) centerFromPrev(cols[c], cols[c - 1])
  for (let c = anchorIdx - 1; c >= 0; c--) positionPreAnchor(cols[c], cols[c + 1], sh)

  markSeeds(cols, partial ? bypassing : 0)
  return {
    columns: cols,
    connectors: buildConnectors(cols),
    totalHeight: computeTotalHeight(cols, sh),
  }
}

function buildBP(breakSize) {
  const six = breakSize % 6 === 0 && isPow2(breakSize / 6)
  const four = breakSize % 4 === 0 && isPow2(breakSize / 4)
  const partial = six && !four
  const bypassing = partial ? Math.floor(breakSize / 3) : 0
  const sh = slotH.value

  const cols = []
  for (let ri = 0; ri < props.rounds.length; ri++) {
    const sr = props.rounds[ri]
    let slots = parseServerSlots(sr)
    if (!slots) {
      let count, startRank = 1
      if (partial && ri === 0) {
        count = Math.round(breakSize / 6)
        startRank = bypassing + 1
      } else if (!partial && ri === 0) {
        count = Math.round(breakSize / 4)
      } else if (partial) {
        count = Math.max(1, Math.round(breakSize / (3 * (1 << ri))))
      } else {
        count = Math.max(1, Math.round(breakSize / (4 * (1 << ri))))
      }
      slots = makePlaceholderSlots(count, startRank)
    }
    slots.sort((a, b) => a.roomRank - b.roomRank)
    cols.push({ name: sr.name, slots })
  }

  inferMissingPairings(cols, breakSize, partial, true)

  const anchorIdx = partial ? Math.min(1, cols.length - 1) : 0
  assignParentRanks(cols, partial, true, breakSize)
  sortAnchor(cols[anchorIdx], sh)
  for (let c = anchorIdx + 1; c < cols.length; c++) centerFromPrev(cols[c], cols[c - 1])
  for (let c = anchorIdx - 1; c >= 0; c--) positionPreAnchor(cols[c], cols[c + 1], sh)

  markSeeds(cols, bypassing)
  return {
    columns: cols,
    connectors: buildConnectors(cols),
    totalHeight: computeTotalHeight(cols, sh),
  }
}

function showSeed(teams) {
  return teams.some(t => t.showSeed)
}

// --- Connector SVG path ---

function connPath(c) {
  const mid = CONNECTOR_W / 2
  return `M 0 ${c.fromY} H ${mid} V ${c.toY} H ${CONNECTOR_W}`
}

function connectorsForCol(idx) {
  return bracket.value?.connectors.filter(c => c.colIndex === idx) ?? []
}
</script>

<template>
  <div v-if="bracket" class="bracket-wrapper">
    <div class="bracket-headers d-flex">
      <template v-for="(col, ci) in bracket.columns" :key="'h'+ci">
        <div class="bracket-round-header" :style="{ width: COL_WIDTH + 'px' }">
          {{ col.name }}
        </div>
        <div v-if="ci < bracket.columns.length - 1"
             :style="{ width: CONNECTOR_W + 'px' }"></div>
      </template>
    </div>

    <div class="bracket-body d-flex align-items-start">
      <template v-for="(col, ci) in bracket.columns" :key="'c'+ci">
        <div class="bracket-round"
             :style="{ width: COL_WIDTH + 'px', height: bracket.totalHeight + 'px' }">
          <div v-for="slot in col.slots" :key="slot.roomRank"
               class="bracket-debate card"
               :class="slot.inferred ? 'border-dashed' : 'shadow-sm'"
               :style="{
                 top: (slot.yCenter - slotH / 2) + 'px',
                 height: slotH + 'px',
               }">
            <template v-if="slot.teams.length">
              <div v-for="(t, ti) in slot.teams" :key="ti"
                   class="bracket-team d-flex align-items-center"
                   :class="{
                     'alert-success': t.advancing === true,
                   }"
                   :style="{ height: (100 / teamsInDebate) + '%' }">
                <span v-if="showSeed(slot.teams)" class="bracket-col-seed text-center">
                  <span v-if="t.showSeed" class="badge bg-secondary bracket-badge">
                    {{ t.showSeed }}
                  </span>
                </span>
                <span v-if="slot.sidesConfirmed" class="bracket-col-side text-center">
                  <span class="text-muted bracket-side-label">{{ sideLabel(t.side) }}</span>
                </span>
                <span class="bracket-col-name text-truncate">
                  <template v-if="t.team">{{ t.team.short_name }}</template>
                  <span v-else class="text-muted">TBD</span>
                </span>
              </div>
            </template>
            <template v-else>
              <div v-for="n in teamsInDebate" :key="n"
                   class="bracket-team d-flex align-items-center text-muted"
                   :style="{ height: (100 / teamsInDebate) + '%' }">
                <span v-if="showSeed(slot.teams)" class="bracket-col-seed"></span>
                <span class="bracket-col-name">TBD</span>
              </div>
            </template>
          </div>
        </div>

        <svg v-if="ci < bracket.columns.length - 1"
             class="bracket-svg"
             :width="CONNECTOR_W"
             :height="bracket.totalHeight">
          <path v-for="(cn, cni) in connectorsForCol(ci)" :key="cni"
                :d="connPath(cn)"
                fill="none" stroke="#bbb" stroke-width="1.5"
                :stroke-dasharray="cn.inferred ? '4 3' : 'none'" />
        </svg>
      </template>
    </div>
  </div>

  <div v-else class="text-muted text-center p-4">
    No bracket data available.
  </div>
</template>

<style scoped lang="scss">
.bracket-wrapper {
  overflow-x: auto;
  padding: 0.5rem;
}
.bracket-headers {
  margin-bottom: 0.25rem;
}
.bracket-round-header {
  text-align: center;
  text-transform: uppercase;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6c757d;
  padding: 0.25rem 0;
  flex-shrink: 0;
}
.bracket-round {
  position: relative;
  flex-shrink: 0;
}
.bracket-debate {
  position: absolute;
  left: 4px;
  right: 4px;
  overflow: hidden;
  border-radius: 4px;

  &.border-dashed {
    border-style: dashed;
  }
}
.bracket-team {
  white-space: nowrap;
  overflow: hidden;
  font-size: 0.82rem;
  line-height: 1.3;
  padding: 0 4px;
  gap: 4px;

  &:not(:last-child) {
    border-bottom: 1px solid #dee2e6;
  }
}
.bracket-col-seed {
  flex: 0 0 22px;
  min-width: 22px;
}
.bracket-col-side {
  flex: 0 0 24px;
  min-width: 24px;
}
.bracket-col-name {
  flex: 1 1 0;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bracket-badge {
  font-size: 0.65rem;
  color: black;
}
.bracket-side-label {
  font-size: 0.7rem;
}
.bracket-svg {
  flex-shrink: 0;
  display: block;
}
</style>
