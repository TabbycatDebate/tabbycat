<script setup>
import { computed, ref, watch } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'

const props = defineProps({
  institutions: Array,
  independentTeams: Array,
  initialMRounds: Number,
  initialStrictMode: Boolean,
  initialInstitutionNEqualsN: Boolean,
  assignmentsUrl: String,
  saveSettingsUrl: String,
  finesUrl: String,
  csrfToken: String,
})

const { gettext } = useDjangoI18n()

const m = ref(props.initialMRounds ?? 3)
const strict = ref(props.initialStrictMode ?? false)
const nEqualsN = ref(props.initialInstitutionNEqualsN ?? false)
const filterCompliance = ref('all')
const viewSection = ref('both')
const expandedId = ref(null)
const saveMsg = ref('')
const saveMsgType = ref('success')
let saveTimer = null

// Local reactive copies of fines so +/- updates reflect immediately
const instFines = ref(Object.fromEntries((props.institutions ?? []).map(i => [i.id, i.fines_paid ?? 0])))
const teamFines = ref(Object.fromEntries((props.independentTeams ?? []).map(t => [t.id, t.fines_paid ?? 0])))

function instRequired(inst) {
  return nEqualsN.value ? inst.team_count : Math.max(0, inst.team_count - 1)
}

function instCoverage(inst) {
  const fines = instFines.value[inst.id] ?? 0
  if (strict.value) {
    const qualifying = inst.assignments.filter(j => j.rounds_judged >= m.value).length
    return qualifying + fines
  }
  const totalRounds = inst.assignments.reduce((s, j) => s + j.rounds_judged, 0)
  // each fine counts as M rounds
  return totalRounds + fines * m.value
}

function instRequiredCoverage(inst) {
  const required = instRequired(inst)
  return strict.value ? required : required * m.value
}

function instCompliant(inst) {
  const required = instRequired(inst)
  if (required === 0) return true
  return instCoverage(inst) >= instRequiredCoverage(inst)
}

function instPartial(inst) {
  const required = instRequired(inst)
  if (required === 0) return false
  const fines = instFines.value[inst.id] ?? 0
  return !instCompliant(inst) && fines > 0
}

function teamCompliant(team) {
  const fines = teamFines.value[team.id] ?? 0
  const hasJudge = !!team.assigned_adj && team.assigned_adj.rounds_judged >= m.value
  return hasJudge || fines >= 1
}

function instStatusClass(inst) {
  if (instCompliant(inst)) return 'badge-success'
  if (instPartial(inst)) return 'badge-warning'
  return 'badge-danger'
}

function instStatusIcon(inst) {
  if (instCompliant(inst)) return '✓'
  if (instPartial(inst)) return '⚠'
  return '✗'
}

function matchesFilter(compliant, partial) {
  if (filterCompliance.value === 'complying') return compliant
  if (filterCompliance.value === 'notComplying') return !compliant
  return true
}

const filteredInstitutions = computed(() =>
  (props.institutions ?? []).filter(inst =>
    matchesFilter(instCompliant(inst), instPartial(inst)),
  ),
)

const filteredTeams = computed(() =>
  (props.independentTeams ?? []).filter(team =>
    matchesFilter(teamCompliant(team), false),
  ),
)

const showInstitutions = computed(() =>
  viewSection.value === 'both' || viewSection.value === 'institutions',
)
const showTeams = computed(() =>
  viewSection.value === 'both' || viewSection.value === 'teams',
)

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

async function saveSettings() {
  try {
    const body = new FormData()
    body.append('csrfmiddlewaretoken', props.csrfToken)
    body.append('m_rounds', m.value)
    body.append('strict_mode', strict.value ? '1' : '0')
    body.append('institution_n_equals_n', nEqualsN.value ? '1' : '0')
    const res = await fetch(props.saveSettingsUrl, { method: 'POST', body })
    saveMsg.value = res.ok ? gettext('Saved') : gettext('Error saving')
    saveMsgType.value = res.ok ? 'success' : 'error'
  } catch {
    saveMsg.value = gettext('Error saving')
    saveMsgType.value = 'error'
  }
  setTimeout(() => { saveMsg.value = '' }, 2000)
}

watch([m, strict, nEqualsN], () => {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(saveSettings, 600)
}, { flush: 'post' })

async function updateFines(payload) {
  try {
    const res = await fetch(props.finesUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': props.csrfToken,
      },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      console.error('Failed to save fine payment')
    }
  } catch {
    console.error('Network error saving fine payment')
  }
}

function changeInstFines(inst, delta) {
  const current = instFines.value[inst.id] ?? 0
  const next = Math.max(0, current + delta)
  instFines.value[inst.id] = next
  updateFines({ institution_id: inst.id, fines_paid: next })
}

function changeTeamFines(team, delta) {
  const current = teamFines.value[team.id] ?? 0
  const next = Math.max(0, current + delta)
  teamFines.value[team.id] = next
  updateFines({ team_id: team.id, fines_paid: next })
}
</script>

<template>
  <div>
    <!-- Settings panel -->
    <div class="card mb-3">
      <div class="card-body py-3">
        <div class="d-flex flex-wrap align-items-center gap-3">
          <div class="d-flex align-items-center">
            <label class="mb-0 mr-2 font-weight-bold">{{ gettext('Minimum rounds (M):') }}</label>
            <input
              v-model.number="m"
              type="number"
              class="form-control form-control-sm"
              style="width:70px"
              min="1"
            >
          </div>

          <div class="d-flex align-items-center">
            <div
              class="btn-group"
              role="group"
            >
              <button
                type="button"
                class="btn btn-sm"
                :class="strict ? 'btn-outline-secondary' : 'btn-primary'"
                @click="strict = false"
              >
                {{ gettext('Non-strict') }}
              </button>
              <button
                type="button"
                class="btn btn-sm"
                :class="strict ? 'btn-primary' : 'btn-outline-secondary'"
                @click="strict = true"
              >
                {{ gettext('Strict') }}
              </button>
            </div>
            <small class="text-muted ml-2">
              <span v-if="strict">{{ gettext('Each judge must individually cover M rounds') }}</span>
              <span v-else>{{ gettext('Total rounds across judges ≥ required × M') }}</span>
            </small>
          </div>

          <div class="d-flex align-items-center">
            <div
              class="btn-group"
              role="group"
            >
              <button
                type="button"
                class="btn btn-sm"
                :class="nEqualsN ? 'btn-outline-secondary' : 'btn-primary'"
                @click="nEqualsN = false"
              >
                {{ gettext('N-1') }}
              </button>
              <button
                type="button"
                class="btn btn-sm"
                :class="nEqualsN ? 'btn-primary' : 'btn-outline-secondary'"
                @click="nEqualsN = true"
              >
                {{ gettext('N=N') }}
              </button>
            </div>
            <small class="text-muted ml-2">
              <span v-if="nEqualsN">{{ gettext('Institutions must provide N judges for N teams') }}</span>
              <span v-else>{{ gettext('Institutions must provide N-1 judges for N teams') }}</span>
            </small>
          </div>

          <span
            v-if="saveMsg"
            class="small"
            :class="saveMsgType === 'success' ? 'text-success' : 'text-danger'"
          >{{ saveMsg }}</span>

          <a
            :href="assignmentsUrl"
            class="btn btn-sm btn-outline-secondary ml-auto"
          >
            {{ gettext('Edit Assignments') }}
          </a>
        </div>
      </div>
    </div>

    <!-- Filter controls -->
    <div
      class="d-flex flex-wrap mb-3"
      style="gap:0.5rem"
    >
      <div
        class="btn-group"
        role="group"
      >
        <button
          type="button"
          class="btn btn-sm"
          :class="filterCompliance === 'all' ? 'btn-primary' : 'btn-outline-secondary'"
          @click="filterCompliance = 'all'"
        >
          {{ gettext('All') }}
        </button>
        <button
          type="button"
          class="btn btn-sm"
          :class="filterCompliance === 'complying' ? 'btn-success' : 'btn-outline-secondary'"
          @click="filterCompliance = 'complying'"
        >
          {{ gettext('Complying') }}
        </button>
        <button
          type="button"
          class="btn btn-sm"
          :class="filterCompliance === 'notComplying' ? 'btn-danger' : 'btn-outline-secondary'"
          @click="filterCompliance = 'notComplying'"
        >
          {{ gettext('Not complying') }}
        </button>
      </div>
      <div
        class="btn-group"
        role="group"
      >
        <button
          type="button"
          class="btn btn-sm"
          :class="viewSection === 'both' ? 'btn-primary' : 'btn-outline-secondary'"
          @click="viewSection = 'both'"
        >
          {{ gettext('Both') }}
        </button>
        <button
          type="button"
          class="btn btn-sm"
          :class="viewSection === 'institutions' ? 'btn-primary' : 'btn-outline-secondary'"
          @click="viewSection = 'institutions'"
        >
          {{ gettext('Institutions') }}
        </button>
        <button
          type="button"
          class="btn btn-sm"
          :class="viewSection === 'teams' ? 'btn-primary' : 'btn-outline-secondary'"
          @click="viewSection = 'teams'"
        >
          {{ gettext('Independent Teams') }}
        </button>
      </div>
    </div>

    <!-- Institutions section -->
    <template v-if="showInstitutions">
      <h5 class="mt-3">
        {{ gettext('Institutions') }}
      </h5>
      <p
        v-if="filteredInstitutions.length === 0"
        class="text-muted"
      >
        {{ gettext('No institutions to show.') }}
      </p>
      <div class="card mt-1">
        <div
          v-for="inst in filteredInstitutions"
          :key="inst.id"
          class="list-group-item list-group-item-action p-0"
        >
          <div
            class="d-flex align-items-center px-3 py-2"
            style="cursor:pointer"
            @click="toggleExpand('inst-' + inst.id)"
          >
            <span
              class="badge mr-2"
              :class="instStatusClass(inst)"
            >
              {{ instStatusIcon(inst) }}
            </span>
            <strong>{{ inst.name }}</strong>
            <span class="text-muted ml-2 small">
              {{ inst.team_count }} {{ inst.team_count !== 1 ? gettext('teams') : gettext('team') }}
              · {{ gettext('needs') }} {{ instRequired(inst) }} {{ instRequired(inst) !== 1 ? gettext('judges') : gettext('judge') }}
              ({{ nEqualsN ? gettext('N=N') : gettext('N-1') }})
              · {{ inst.assignments.length }} {{ gettext('assigned') }}
            </span>
            <span class="ml-auto text-muted small">
              {{ expandedId === 'inst-' + inst.id ? '▲' : '▼' }}
            </span>
          </div>
          <div
            v-if="expandedId === 'inst-' + inst.id"
            class="border-top"
          >
            <div
              v-if="inst.assignments.length === 0"
              class="px-3 py-2 text-muted small"
            >
              {{ gettext('No judges assigned.') }}
            </div>
            <div
              v-for="j in inst.assignments"
              :key="j.adj_id"
              class="d-flex align-items-center px-3 py-2 border-bottom"
            >
              <span
                class="mr-2"
                :class="j.rounds_judged >= m ? 'text-success' : 'text-danger'"
              >
                {{ j.rounds_judged >= m ? '✓' : '✗' }}
              </span>
              <span>{{ j.adj_name }}</span>
              <span class="ml-auto text-muted small">{{ j.rounds_judged }} / {{ m }} {{ gettext('rounds') }}</span>
            </div>
            <!-- Fines row -->
            <div class="d-flex align-items-center px-3 py-2">
              <span class="text-muted small mr-3">{{ gettext('Fines paid:') }}</span>
              <button
                class="btn btn-sm btn-outline-secondary px-2 py-0"
                :disabled="(instFines[inst.id] ?? 0) === 0"
                @click.stop="changeInstFines(inst, -1)"
              >
                −
              </button>
              <span class="mx-2 font-weight-bold">{{ instFines[inst.id] ?? 0 }}</span>
              <button
                class="btn btn-sm btn-outline-secondary px-2 py-0"
                @click.stop="changeInstFines(inst, +1)"
              >
                +
              </button>
              <span class="text-muted small ml-3">
                ({{ inst.assignments.length }} {{ inst.assignments.length !== 1 ? gettext('judges') : gettext('judge') }}
                + {{ instFines[inst.id] ?? 0 }} {{ (instFines[inst.id] ?? 0) !== 1 ? gettext('fines') : gettext('fine') }}
                / {{ instRequired(inst) }} {{ gettext('required') }})
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Independent teams section -->
    <template v-if="showTeams">
      <h5 class="mt-4">
        {{ gettext('Independent Teams') }}
      </h5>
      <p
        v-if="filteredTeams.length === 0"
        class="text-muted"
      >
        {{ gettext('No independent teams to show.') }}
      </p>
      <div class="card mt-1">
        <div
          v-for="team in filteredTeams"
          :key="team.id"
          class="list-group-item d-flex align-items-center flex-wrap"
          style="gap:0.5rem"
        >
          <span
            class="badge mr-2"
            :class="teamCompliant(team) ? 'badge-success' : 'badge-danger'"
          >
            {{ teamCompliant(team) ? '✓' : '✗' }}
          </span>
          <strong>{{ team.name }}</strong>
          <template v-if="team.assigned_adj">
            <span class="text-muted small">
              {{ team.assigned_adj.name }}
              ({{ team.assigned_adj.rounds_judged }}/{{ m }} {{ gettext('rounds') }})
            </span>
          </template>
          <span
            v-else
            class="text-muted small"
          >{{ gettext('No judge assigned') }}</span>
          <div
            class="d-flex align-items-center ml-auto"
            style="gap:0.25rem"
          >
            <span class="text-muted small">{{ gettext('Fines:') }}</span>
            <button
              class="btn btn-sm btn-outline-secondary px-2 py-0"
              :disabled="(teamFines[team.id] ?? 0) === 0"
              @click="changeTeamFines(team, -1)"
            >
              −
            </button>
            <span class="mx-1 font-weight-bold">{{ teamFines[team.id] ?? 0 }}</span>
            <button
              class="btn btn-sm btn-outline-secondary px-2 py-0"
              @click="changeTeamFines(team, +1)"
            >
              +
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
