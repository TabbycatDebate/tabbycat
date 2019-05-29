<template>
  <div class="db-flex-column db-bordered db-flex-item-half">

    <div class="db-flex-item-2 db-flex-row db-bottom-border">
      <div class="db-padding-horizontal flex-grow-1 db-align-vertical-center">
        <strong v-text="gettext('%1, %2', titleCasePosition, teamName)"></strong>
      </div>
      <div class="db-padding-horizontal db-align-vertical-center strong small" v-if="this.team.iron"
           v-text="gettext('IMPORTANT: Check and explicitly note if a speaker gives multiple speeches')"></div>
      <div class="db-padding-horizontal db-align-vertical-center">
        {{ speakersList }}
      </div>
      <div class="db-padding-horizontal db-flex-static "></div>
    </div>

    <template v-for="pos in this.dt.positions">

      <div class="db-flex-item-3 db-flex-row db-bottom-border">
        <div class="db-flex-item-1 align-items-center d-flex small db-padding-horizontal" v-text="gettext('%1:', pos)"></div>
        <div class="db-fill-in db-flex-item-8 d-flex"></div>
        <div class="db-flex-item-1 align-items-center d-flex small db-padding-horizontal">
          <span v-text="gettext('Score:')"></span>
        </div>
        <div class="db-fill-in db-flex-item-3 d-flex"></div>
      </div>

      <div v-if="roundInfo.showDigits"
           class="db-flex-item-2 align-items-center d-flex pr-1 small db-bottom-border">
        <div class="db-flex-item-2 db-padding-horizontal text-secondary"
             v-text="gettext('Circle the last digit of the %1\'s score:', pos)"></div>
        <div class="db-flex-item-3 d-flex">
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('0')"></span></div>
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('1')"></span></div>
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('2')"></span></div>
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('3')"></span></div>
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('4')"></span></div>
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('5')"></span></div>
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('6')"></span></div>
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('7')"></span></div>
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('8')"></span></div>
          <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('9')"></span></div>
        </div>
      </div>

    </template>

    <div class="db-flex-item-3 db-flex-row db-bottom-border"><!-- Totals -->
      <template v-if="roundInfo.isBP">
        <div class="db-flex-item-2 align-items-center d-flex small db-padding-horizontal" v-text="gettext('Circle Rank:')"></div>
        <div class="db-flex-item-6 db-flex-row">
          <div class="flex-grow-1 db-align-vertical-center db-align-horizontal-center">
            <span class="db-circle text-monospace" v-text="gettext('1st')"></span>
          </div>
          <div class="flex-grow-1 db-align-vertical-center db-align-horizontal-center">
            <span class="db-circle text-monospace" v-text="gettext('2nd')"></span>
          </div>
          <div class="flex-grow-1 db-align-vertical-center db-align-horizontal-center">
            <span class="db-circle text-monospace" v-text="gettext('3rd')"></span>
          </div>
          <div class="flex-grow-1 db-align-vertical-center db-align-horizontal-center">
            <span class="db-circle text-monospace" v-text="gettext('4th')"></span>
          </div>
        </div>
        <div class="db-flex-item-1"><!-- Spacing --></div>
      </template>
      <template v-else>
        <div class="db-flex-item-9 db-padding-horizontal"><!-- Spacing --></div>
      </template>
      <div class="db-flex-item-1 align-items-center d-flex small db-padding-horizontal">
        <span v-text="gettext('Total:')"></span>
      </div>
      <div class="db-fill-in db-flex-item-3 d-flex">

      </div>
    </div>

    <div v-if="roundInfo.showDigits" class="db-flex-item-2 align-items-center d-flex pr-1 small">
      <div class="db-flex-item-2 db-padding-horizontal text-secondary"
           v-text="gettext('Circle the last digit of the team\'s total:')"></div>
      <div class="db-flex-item-3 d-flex">
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('0')"></span></div>
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('1')"></span></div>
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('2')"></span></div>
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('3')"></span></div>
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('4')"></span></div>
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('5')"></span></div>
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('6')"></span></div>
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('7')"></span></div>
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('8')"></span></div>
        <div class="flex-fill text-center"><span class="db-circle" v-text="gettext('9')"></span></div>
      </div>
    </div>

  </div>
</template>

<script>
import _ from 'lodash'

export default {
  props: {
    dt: Object,
    roundInfo: Object,
  },
  computed: {
    team: function () {
      if (this.dt.team !== null) {
        return this.dt.team
      } else {
        // Fallback if no team is assigned
        return {
          code_name: '____________________________________________________________',
          short_name: '____________________________________________________________',
          speakers: [],
        }
      }
    },
    teamName: function () {
      if (this.roundInfo.teamCodes === true) {
        return this.team.code_name
      }
      return this.team.short_name
    },
    speakersList: function () {
      let speakersList = ''
      _.forEach(this.team.speakers, (speaker) => {
        speakersList += `${speaker.name}, `
      })
      return speakersList.slice(0, -2)
    },
    titleCasePosition: function () {
      const upperWords = _.map(_.words(this.dt.side_name), word => _.upperFirst(word))
      return _.join(upperWords, ' ')
    },
  },
}
</script>
