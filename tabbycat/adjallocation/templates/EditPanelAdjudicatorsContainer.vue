<template>

  <drag-and-drop-layout :unallocatedItems="unallocatedItems"
                        :unallocatedComponent="unallocatedComponent"
                        :handle-unused-drop="moveAdjudicator">

    <drag-and-drop-actions slot="actions" :count="debatesOrPanelsCount" prioritise="true" allocate="true" shard="true"
                           @show-shard="showShard" @show-allocate="showAllocate" @show-prioritise="showPrioritise">
      <template slot="extra-actions">
        <button :class="['btn', debatesOrPanelsCount > 0 ? 'btn-outline-primary' : 'btn-success']"
                @click="showCreatePanels" v-text="gettext('Create Panels')"></button>
      </template>
      <template slot="default-highlights">
        <button class="btn conflictable conflicts-toolbar hover-histories-2-ago"
                data-toggle="tooltip" v-text="gettext('Seen')"
                title="This adjudicator has judged with this adjudicator previously"></button>
        <button class="btn conflictable conflicts-toolbar hover-institution"
                data-toggle="tooltip" v-text="gettext('Institution')"
                title="This adjudicator is from the same institution as this panelist."></button>
        <button class="btn conflictable conflicts-toolbar hover-adjudicator"
                data-toggle="tooltip" v-text="gettext('Conflict')"
                title="This adjudicator has a nominated conflict with this panelist."></button>
        <button class="btn panel-incomplete"
                data-toggle="tooltip" v-text="gettext('Missing')"
                title="Panel is either missing a chair or enough adjudicators for a voting majority."></button>
      </template>
    </drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="panel in sortedDebatesOrPanels" :key="panel.pk" :debateOrPanel="panel">
        <debate-or-panel-importance slot="importance"
                                    :debate-or-panel="panel"></debate-or-panel-importance>
        <debate-or-panel-adjudicators slot="adjudicators" :debate-or-panel="panel"
                                      :handle-debate-or-panel-drop="moveAdjudicator">
        </debate-or-panel-adjudicators>
        <template slot="teams"><span></span></template><!--Hide Teams-->
        <template slot="venue"><span></span></template><!--Hide Venues-->
      </drag-and-drop-debate>
      <div class="text-center lead mx-5 p-5" v-if="debatesOrPanelsCount === 0">
        <p class="mx-5 lead mt-2 px-5" v-text="gettext(createPanelsInline)"></p>
      </div>
    </template>

    <template slot="modals">
      <modal-for-creating-preformed-panels :context-of-action="'create_preformed_panels'">
      </modal-for-creating-preformed-panels>
      <modal-for-sharding :intro-text="gettext(shardIntro)"></modal-for-sharding>
      <modal-for-allocating :intro-text="gettext(allocateIntro)" :for-panels="true"
                            :context-of-action="'allocate_panel_adjs'"></modal-for-allocating>
      <modal-for-prioritising :intro-text="gettext(prioritiseIntro)"
                              :context-of-action="'prioritise_panels'"></modal-for-prioritising>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import ModalForCreatingPreformedPanels from '../../templates/modals/ModalForCreatingPreformedPanels.vue'

import EditEitherAdjudicatorsSharedMixin from './EditEitherAdjudicatorsSharedMixin.vue'

export default {
  mixins: [EditEitherAdjudicatorsSharedMixin],
  components: {
    ModalForCreatingPreformedPanels,
  },
  data: () => ({
    sockets: ['panels'], // Override the normal debate socket from DragAndDropContainerMixin
    shardIntro: `Sharding narrows the debates displayed to show only a specific subset of the
      overall draw`,
    allocateIntro: `Using auto-allocate will remove adjudicators from panels and create a new
      allocations in their place.`,
    prioritiseIntro: `Using auto-prioritise will remove all existing panel priorities and
      assign new ones.`,
    createPanelsInline: `There are no Preformed Panels for this round. You will need to create
      some first by using the button in the top-left.`,
  }),
  methods: {
    showCreatePanels: function () {
      $('#confirmCreatePreformedPanelsModal').modal('show')
    },
  },
}
</script>
