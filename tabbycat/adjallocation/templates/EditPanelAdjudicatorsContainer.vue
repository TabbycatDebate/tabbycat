<template>

  <drag-and-drop-layout>

    <drag-and-drop-actions slot="actions" prioritise="true" allocate="true" shard="true"
                           @shard="shard" @allocate="allocate" @prioritise="prioritise">
      <template slot="default-highlights">
        <button class="btn btn-outline-secondary disabled" v-text="gettext('Key')"></button>
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
                data-toggle="tooltip" v-text="gettext('Incomplete')"
                title="Panel is eithr missing a chair or enough adjudicators for a voting majority."></button>
      </template>
    </drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="panel in debatesOrPanels" :key="panel.pk" :debateOrPanel="panel">
        <debate-importance slot="importance" :debateOrPanel="panel"></debate-importance>
        <template slot="adjudicators">fancy adjs UI</template>
        <template slot="venue"><span></span></template><!--Hide Venues-->
      </drag-and-drop-debate>
    </template>

    <template slot="modals">
      <modal-for-sharding :intro-text="gettext('shardIntro')"></modal-for-sharding>
      <modal-for-allocating :intro-text="gettext(allocateIntro)"
                            :context-of-action="'allocate_panel_adjs'"></modal-for-allocating>
      <modal-for-prioritising :intro-text="gettext(prioritiseIntro)"
                              :context-of-action="'prioritise_panel_adjs'"></modal-for-prioritising>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import EditEitherAdjudicatorsSharedMixin from './EditEitherAdjudicatorsSharedMixin.vue'

export default {
  mixins: [EditEitherAdjudicatorsSharedMixin],
  data: () => ({
    sockets: ['panels'], // Override the normal debate socket from DragAndDropContainerMixin
    shardIntro: `Sharding narrows the debates displayed to show only a specific subset of the
      overall draw`,
    allocateIntro: `Using auto-allocate will remove adjudicators from panels and create a new
      allocations in their place.`,
    prioritiseIntro: `Using auto-prioritise will remove all existing panel priorities and
      assign new ones.`,
  }),
}
</script>
