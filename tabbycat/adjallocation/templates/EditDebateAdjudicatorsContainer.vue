<template>

  <drag-and-drop-layout :unallocatedItems="unallocatedItems"
                        :unallocatedComponent="unallocatedComponent"
                        :handle-unused-drop="moveAdjudicator">

    <drag-and-drop-actions slot="actions" :count="debatesOrPanelsCount" prioritise="true" allocate="true" shard="true"
                           @show-shard="showShard" @show-allocate="showAllocate" @show-prioritise="showPrioritise">
      <template slot="default-highlights">
        <button class="btn conflictable conflicts-toolbar hover-histories-2-ago"
                data-toggle="tooltip" v-text="gettext('Seen')"
                :title="('Has judged this team or with this adjudicator previously')"></button>
        <button class="btn conflictable conflicts-toolbar hover-institution"
                data-toggle="tooltip" v-text="gettext('Institution')"
                :title="('Is from the same institution as this team or panelist.')"></button>
        <button class="btn conflictable conflicts-toolbar hover-adjudicator"
                data-toggle="tooltip" v-text="gettext('Conflict')"
                :title="('Has a nominated conflict with this team or panelist.')"></button>
        <button class="btn panel-incomplete"
                data-toggle="tooltip" v-text="gettext('Missing')"
                :title="('Panel is missing a chair or enough adjudicators for a voting majority.')"></button>
      </template>
    </drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="debate in sortedDebatesOrPanels" :key="debate.id" :debateOrPanel="debate">
        <debate-or-panel-importance slot="importance" :debate-or-panel="debate"></debate-or-panel-importance>
        <debate-or-panel-adjudicators slot="adjudicators" :debate-or-panel="debate"
                                      :handle-debate-or-panel-drop="moveAdjudicator">
        </debate-or-panel-adjudicators>
        <template slot="venue"><span></span></template><!--Hide Venues-->
      </drag-and-drop-debate>
      <div class="text-center lead mx-5 p-5" v-if="sortedDebatesOrPanels.length === 0">
        <p class="mx-5 lead mt-2 px-5" v-text="gettext(noDebatesInline)"></p>
      </div>
    </template>

    <template slot="modals">
      <modal-for-sharding :intro-text="gettext(intro)"></modal-for-sharding>
      <modal-for-allocating :intro-text="gettext(allocateIntro)"
                            :context-of-action="'allocate_debate_adjs'"></modal-for-allocating>
      <modal-for-prioritising :intro-text="gettext(prioritiseIntro)"
                              :context-of-action="'prioritise_debates'"></modal-for-prioritising>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import EditEitherAdjudicatorsSharedMixin from './EditEitherAdjudicatorsSharedMixin.vue'

export default {
  mixins: [EditEitherAdjudicatorsSharedMixin],
  data: () => ({
    intro: `Sharding narrows the panels displayed to show only a specific subset of all
      panels available.`,
    allocateIntro: `Using auto-allocate will remove adjudicators from all debates and create a new
      allocations in their place.`,
    prioritiseIntro: `Using auto-prioritise will remove all existing debate priorities and assign
      new ones.`,
    noDebatesInline: 'There are no debates created for this round.',
  }),
}
</script>
