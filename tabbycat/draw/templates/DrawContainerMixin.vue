<script>
// Note the data/props/computed setup as per https://vuejs.org/v2/guide/components.html
// Props are passed down from root; but we need to cast them into data
// so that it can then mutate them here in response to children
import _ from 'lodash'
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'
import UnallocatedItemsContainer from '../../templates/draganddrops/UnallocatedItemsContainer.vue'
import DrawHeader from '../../templates/draw/DrawHeader.vue'
import Debate from '../../templates/draw/Debate.vue'
import AutoSaveCounter from '../../templates/draganddrops/AutoSaveCounter.vue'
import DroppableGeneric from '../../templates/draganddrops/DroppableGeneric.vue'
import ShardContainerMixin from '../../templates/allocations/ShardContainerMixin.vue'
import SlideOverContainerMixin from '../../templates/info/SlideOverContainerMixin.vue'
import SlideOver from '../../templates/info/SlideOver.vue'
import SortableTableMixin from '../../templates/tables/SortableTableMixin.vue'

export default {
  mixins: [AjaxMixin, SlideOverContainerMixin, SortableTableMixin, ShardContainerMixin],
  components: {
    DrawHeader,
    AutoSaveCounter,
    Debate,
    DroppableGeneric,
    UnallocatedItemsContainer,
    SlideOver,
  },
  data: function () {
    return {
      debates: this.initialDebates,
      unallocatedItems: this.initialUnallocatedItems,
      headers: [
        { key: 'bracket' }, { key: 'liveness' }, { key: 'importance' },
        { key: 'venue' }, { key: 'aff' }, { key: 'neg' },
        { key: 'og' }, { key: 'oo' }, { key: 'cg' }, { key: 'co' },
      ],
    }
  },
  props: ['initialDebates', 'initialUnallocatedItems', 'roundInfo'],
  created: function () {
    // Watch for events on the global event hub
    this.$eventHub.$on('unassign-draggable', this.moveToUnused)
    this.$eventHub.$on('assign-draggable', this.moveToDebate)
    this.$eventHub.$on('update-allocation', this.updateDebates)
    this.$eventHub.$on('update-unallocated', this.updateUnallocatedItems)
  },
  computed: {
    sortableData: function () {
      return this.debatesWithSharding // Enables SortableTableMixin
    },
    teams: function () {
      // Return all teams (in debates) as a single array
      const allTeams = _.map(this.debates, debate => _.map(debate.debateTeams, dt => dt.team))
      return _.flattenDeep(allTeams)
    },
    adjudicators: function () {
      // Return all adjs (in debates) as a single array
      const allPanellists = _.map(this.debates, debate =>
        _.map(debate.debateAdjudicators, p => p.adjudicator))
      const allAdjudicators = allPanellists.concat(this.unallocatedItems)
      return _.flattenDeep(allAdjudicators)
    },
    venues: function () {
      // Return all teams as a single array
      const allVenues = _.map(this.debates, debate => debate.venue)
      return allVenues
    },
    debatesById: function () {
      return _.keyBy(this.debates, 'id')
    },
    teamsById: function () {
      return _.keyBy(this.teams, 'id')
    },
    adjudicatorsById: function () {
      return _.keyBy(this.adjudicators, 'id')
    },
    institutionsById: function () {
      const teamInstitutions = this.teams.map((team) => {
        if (team !== null) {
          return team.institution
        }
        return false
      })
      const adjInstitutions = _.map(this.adjudicators, adjudicator => adjudicator.institution)
      const allInstitutions = teamInstitutions.concat(adjInstitutions)
      const uniqueInstitutions = _.uniq(allInstitutions)
      return _.keyBy(uniqueInstitutions, 'id')
    },
    unallocatedById: function () {
      return _.keyBy(this.unallocatedItems, 'id')
    },
    teamPositions: function () {
      return this.roundInfo.teamPositions // Convenience
    },
  },
  methods: {
    updateDebates: function (updatedDebates) {
      this.debates = updatedDebates // Match internal data to json response
    },
    updateUnallocatedItems: function (updatedUnallocatedItems) {
      this.unallocatedItems = updatedUnallocatedItems // As above
    },
    // Duplicating sortableHeaderMixin; but can't inheret in a slot
    sortClasses: function (key) {
      const baseCSS = 'vue-sort-key '
      if (!_.isUndefined(this.sortKey) && !_.isUndefined(key)) {
        if (this.sortKey.toLowerCase() === key.toLowerCase()) {
          if (this.sortOrder === 'asc') {
            return `${baseCSS}vue-sort-active sort-by-desc`
          }
          return `${baseCSS}vue-sort-active sort-by-asc`
        }
      }
      return `${baseCSS}text-muted`
    },
    getSortableProperty (row) {
      // Rather than an array of cells (as in Table) row is a Debate
      // So just return the relevant property
      const key = this.sortKey
      if (typeof row[key] === 'string' ||
          typeof row[key] === 'number') {
        return row[key]
      } else if (key === 'venue') {
        if (!_.isNull(row.venue)) {
          return row.venue.name
        }
        return '' // Venues can be null
      } else if (_.includes(_.map(this.teamPositions), key)) {
        const teamAtSide = _.find(row.debateTeams, dt => dt.side === key)
        if (teamAtSide.team !== null) {
          return teamAtSide.team.short_name
        }
        return '' // Teams in a position can be null
      }
      console.error('Couldnt find sorting property')
      return '' // Teams in a position can be null
    },
  },
}
</script>
