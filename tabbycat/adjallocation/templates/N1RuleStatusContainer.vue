<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  institutions: Array,
  independentTeams: Array,
  initialMRounds: Number,
  initialStrictMode: Boolean,
  assignmentsUrl: String,
  saveSettingsUrl: String,
  csrfToken: String,
})

const m = ref(props.initialMRounds ?? 3)
const strict = ref(props.initialStrictMode ?? false)
const filterCompliance = ref('all')
const viewSection = ref('both')
const expandedId = ref(null)
const saving = ref(false)
const saveMsg = ref('')

function instRequired(inst) {
  return Math.max(0, inst.team_count - 1)
}

function instCompliant(inst) {
  const required = instRequired(inst)
  if (required === 0) return true
  if (strict.value) {
    return inst.assignments.filter(j => j.rounds_judged >= m.value).length >= required
  }
  const total = inst.assignments.reduce((s, j) => s + j.rounds_judged, 0)
  return total >= required * m.value
}

function teamCompliant(team) {
  return !!team.assigned_adj && team.assigned_adj.rounds_judged >= m.value
}

function matchesFilter(compliant) {
  if (filterCompliance.value === 'complying') return compliant
  if (filterCompliance.value === 'notComplying') return !compliant
  return true
}

const filteredInstitutions = computed(() =>
  (props.institutions ?? []).filter(inst => matchesFilter(instCompliant(inst)))
)

const filteredTeams = computed(() =>
  (props.independentTeams ?? []).filter(team => matchesFilter(teamCompliant(team)))
)

const showInstitutions = computed(() =>
  viewSection.value === 'both' || viewSection.value === 'institutions'
)
const showTeams = computed(() =>
  viewSection.value === 'both' || viewSection.value === 'teams'
)

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

async function saveSettings() {
  saving.value = true
  saveMsg.value = ''
  try {
    const body = new FormData()
    body.append('csrfmiddlewaretoken', props.csrfToken)
    body.append('m_rounds', m.value)
    body.append('strict_mode', strict.value ? '1' : '0')
    const res = await fetch(props.saveSettingsUrl, { method: 'POST', body })
    if (res.ok) {
      saveMsg.value = 'Saved'
      setTimeout(() => { saveMsg.value = '' }, 2000)
    } else {
      saveMsg.value = 'Error saving'
    }
  } catch {
    saveMsg.value = 'Error saving'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>

    <!-- Settings panel -->
    <div class="card mb-3">
      <div class="card-body py-3">
        <div class="d-flex flex-wrap align-items-center gap-3">

          <div class="d-flex align-items-center">
            <label class="mb-0 mr-2 font-weight-bold">Minimum rounds (M):</label>
            <input type="number" class="form-control form-control-sm" style="width:70px"
                   v-model.number="m" min="1" />
          </div>

          <div class="d-flex align-items-center">
            <div class="btn-group" role="group">
              <button type="button" class="btn btn-sm"
                      :class="strict ? 'btn-outline-secondary' : 'btn-primary'"
                      @click="strict = false">Non-strict</button>
              <button type="button" class="btn btn-sm"
                      :class="strict ? 'btn-primary' : 'btn-outline-secondary'"
                      @click="strict = true">Strict</button>
            </div>
            <small class="text-muted ml-2">
              <span v-if="strict">Each judge must individually cover M rounds</span>
              <span v-else>Total rounds across judges ≥ (N-1) × M</span>
            </small>
          </div>

          <button class="btn btn-sm btn-success" :disabled="saving" @click="saveSettings">
            {{ saving ? 'Saving…' : 'Save settings' }}
          </button>
          <span v-if="saveMsg" class="text-success small">{{ saveMsg }}</span>

          <a :href="assignmentsUrl" class="btn btn-sm btn-outline-secondary ml-auto">
            Edit Assignments
          </a>
        </div>
      </div>
    </div>

    <!-- Filter controls -->
    <div class="d-flex flex-wrap mb-3" style="gap:0.5rem">
      <div class="btn-group" role="group">
        <button type="button" class="btn btn-sm"
                :class="filterCompliance === 'all' ? 'btn-primary' : 'btn-outline-secondary'"
                @click="filterCompliance = 'all'">All</button>
        <button type="button" class="btn btn-sm"
                :class="filterCompliance === 'complying' ? 'btn-success' : 'btn-outline-secondary'"
                @click="filterCompliance = 'complying'">Complying</button>
        <button type="button" class="btn btn-sm"
                :class="filterCompliance === 'notComplying' ? 'btn-danger' : 'btn-outline-secondary'"
                @click="filterCompliance = 'notComplying'">Not complying</button>
      </div>
      <div class="btn-group" role="group">
        <button type="button" class="btn btn-sm"
                :class="viewSection === 'both' ? 'btn-primary' : 'btn-outline-secondary'"
                @click="viewSection = 'both'">Both</button>
        <button type="button" class="btn btn-sm"
                :class="viewSection === 'institutions' ? 'btn-primary' : 'btn-outline-secondary'"
                @click="viewSection = 'institutions'">Institutions</button>
        <button type="button" class="btn btn-sm"
                :class="viewSection === 'teams' ? 'btn-primary' : 'btn-outline-secondary'"
                @click="viewSection = 'teams'">Independent Teams</button>
      </div>
    </div>

    <!-- Institutions section -->
    <template v-if="showInstitutions">
      <h5 class="mt-3">Institutions</h5>
      <p v-if="filteredInstitutions.length === 0" class="text-muted">No institutions to show.</p>
      <div class="card mt-1">
        <div v-for="inst in filteredInstitutions" :key="inst.id"
             class="list-group-item list-group-item-action p-0">
          <div class="d-flex align-items-center px-3 py-2"
               style="cursor:pointer" @click="toggleExpand('inst-' + inst.id)">
            <span class="badge mr-2"
                  :class="instCompliant(inst) ? 'badge-success' : 'badge-danger'">
              {{ instCompliant(inst) ? '✓' : '✗' }}
            </span>
            <strong>{{ inst.name }}</strong>
            <span class="text-muted ml-2 small">
              {{ inst.team_count }} team{{ inst.team_count !== 1 ? 's' : '' }}
              · needs {{ instRequired(inst) }} judge{{ instRequired(inst) !== 1 ? 's' : '' }}
              · {{ inst.assignments.length }} assigned
            </span>
            <span class="ml-auto text-muted small">
              {{ expandedId === 'inst-' + inst.id ? '▲' : '▼' }}
            </span>
          </div>
          <div v-if="expandedId === 'inst-' + inst.id" class="border-top">
            <div v-if="inst.assignments.length === 0" class="px-3 py-2 text-muted small">
              No judges assigned.
            </div>
            <div v-for="j in inst.assignments" :key="j.adj_id"
                 class="d-flex align-items-center px-3 py-2 border-bottom">
              <span class="mr-2" :class="j.rounds_judged >= m ? 'text-success' : 'text-danger'">
                {{ j.rounds_judged >= m ? '✓' : '✗' }}
              </span>
              <span>{{ j.adj_name }}</span>
              <span class="ml-auto text-muted small">{{ j.rounds_judged }} / {{ m }} rounds</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Independent teams section -->
    <template v-if="showTeams">
      <h5 class="mt-4">Independent Teams</h5>
      <p v-if="filteredTeams.length === 0" class="text-muted">No independent teams to show.</p>
      <div class="card mt-1">
        <div v-for="team in filteredTeams" :key="team.id"
             class="list-group-item d-flex align-items-center">
          <span class="badge mr-2"
                :class="teamCompliant(team) ? 'badge-success' : 'badge-danger'">
            {{ teamCompliant(team) ? '✓' : '✗' }}
          </span>
          <strong>{{ team.name }}</strong>
          <template v-if="team.assigned_adj">
            <span class="ml-2 text-muted small">
              {{ team.assigned_adj.name }}
              ({{ team.assigned_adj.rounds_judged }}/{{ m }} rounds)
            </span>
          </template>
          <span v-else class="ml-2 text-muted small">No judge assigned</span>
        </div>
      </div>
    </template>

  </div>
</template>