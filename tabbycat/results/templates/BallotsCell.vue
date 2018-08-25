

<template>

  <td>

    <div class="flex-vertical-center flex-column">
      <div v-for="ballot in cellData.ballots">
        <a :href="ballotLink(ballot)" class="ballot-link">
          <del v-if="ballot.discarded">
            {{ ballotText(ballot) }} v{{ ballot.version }}
          </del>
          <span v-else>
            {{ ballotText(ballot) }} v{{ ballot.version }}
          </span>
        </a>
        <span class="text-monospace small">{{ ballot.short_time }}</span>
        <span class="small"> by {{ ballot.submitter }}</span>
      </div>
    </div>

  </td>

</template>

<script>

export default {
  props: {
    cellData: Object,
  },
  methods: {
    ballotLink: function(ballot) {
      if (this.cellData.admin) {
        return ballot.admin_link
      }
      return ballot.assistant_link
    },
    ballotText: function(ballot) {
      if (ballot.confirmed) {
        return "Re-Edit"
      } else if (this.cellData.admin) {
        return "Edit"
      } else {
        return "Review"
      }
    }
  },
}

</script>