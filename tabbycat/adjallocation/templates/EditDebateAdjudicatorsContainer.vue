<template>

  <drag-and-drop-layout>

    <drag-and-drop-actions slot="actions" prioritise="#confirmAutoPrioritiseModal"
                           allocate="#confirmAutoAllocationModal">
      <template slot="default-highlights">
        <button class="btn conflictable conflicts-toolbar hover-histories-2-ago"
                data-toggle="tooltip" v-text="gettext('Seen')"
                :title="('This adjudicator has judged this team or judged with this adjudicator previously')"></button>
        <button class="btn conflictable conflicts-toolbar hover-institution"
                data-toggle="tooltip" v-text="gettext('Institution')"
                :title="('This adjudicator is from the same institution as this team or panelist.')"></button>
        <button class="btn conflictable conflicts-toolbar hover-adjudicator"
                data-toggle="tooltip" v-text="gettext('Conflict')"
                :title="('This adjudicator has a nominated conflict with this team or panelist.')"></button>
        <button class="btn panel-incomplete"
                data-toggle="tooltip" v-text="gettext('Incomplete')"
                :title="('Panel is missing a chair or lacks enough adjudicators for a voting majority.')"></button>
      </template>
    </drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="debate in debatesOrPanels" :key="debate.id" :debateOrPanel="debate">
        <debate-importance slot="importance" :debateOrPanel="debate"></debate-importance>
        <template slot="adjudicators">fancy adjs UI</template>
        <template slot="venue"><span></span></template><!--Hide Venues-->
      </drag-and-drop-debate>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import EditEitherAdjudicatorsSharedMixin from './EditEitherAdjudicatorsSharedMixin.vue'

export default {
  mixins: [EditEitherAdjudicatorsSharedMixin],
}
</script>
