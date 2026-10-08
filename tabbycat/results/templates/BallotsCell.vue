<script setup>
import { computed } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'


const props = defineProps({
  cellData: Object,
})

const { gettext } = useDjangoI18n()

const viableBallotsCount = computed(() => {
  return props.cellData.ballots.map((b) => {
    if (b.discarded) {
      return 1
    }
    return 0
  }).reduce((a, b) => a + b, 0)
})

const needsNewBallot = computed(() => {
  return viableBallotsCount.value === props.cellData.ballots.length
})

const canMergeCreate = computed(() => {
  return props.cellData.ballots.some((b) => !b.discarded && b.single_adj)
})

const canReviewBallot = (ballot) => {
  if (props.cellData.acting_role === 'admin') {
    return true
  }
  if (props.cellData.current_user !== ballot.submitter) {
    return true
  }
  return false
}

const ballotLink = (ballot) => {
  if (props.cellData.acting_role === 'admin') {
    return ballot.admin_link
  }
  return ballot.assistant_link
}

const ballotText = (ballot) => {
  if (ballot.confirmed) {
    return gettext('Re-Edit')
  }
  return gettext('Review')
}
</script>

<template>
  <td>
    <div class="ballot-cell pr-2">
      <div
        v-for="ballot in cellData.ballots"
        :key="ballot.id"
      >
        <!-- If ballot was not entered by current user or user is admin -->
        <a
          v-if="canReviewBallot(ballot)"
          :href="ballotLink(ballot)"
          class="ballot-link"
        >
          <del v-if="ballot.discarded">
            {{ ballotText(ballot) }} v{{ ballot.version }}
          </del>
          <span v-else>
            {{ ballotText(ballot) }} v{{ ballot.version }}
          </span>
        </a>

        <!-- If the ballot was entered by current user -->
        <span
          v-else
          class="ballot-link"
          data-toggle="tooltip"
          :title="gettext('You cannot confirm this ballot because you entered it')"
        >
          <del v-if="ballot.discarded">
            {{ ballotText(ballot) }} v{{ ballot.version }}
          </del>
          <span v-else>
            {{ ballotText(ballot) }} v{{ ballot.version }}
          </span>
        </span>

        <!-- Ballot metadata -->
        <span class="small text-muted ballot-info">
          <span class="text-monospace">{{ ballot.short_time }}</span>&nbsp;
          <span
            v-if="ballot.private_url"
            class="text-info"
          >{{ ballot.submitter }}</span>
          <span v-else>{{ ballot.submitter }}</span>
        </span>
      </div>

      <div v-if="canMergeCreate">
        <a :href="cellData.merge_ballot">{{ gettext('Merge Ballot(s)') }}</a>
      </div>

      <div v-if="needsNewBallot">
        <a :href="cellData.new_ballot">{{ gettext('Add Ballot') }}</a>
      </div>
    </div>
  </td>
</template>
