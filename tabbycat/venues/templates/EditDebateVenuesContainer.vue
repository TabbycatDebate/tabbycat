<template>

  <drag-and-drop-layout>

    <drag-and-drop-actions slot="actions" allocate="true" @allocate="allocate">
      <template slot="default-highlights">
        <button class="btn btn-outline-secondary disabled" v-text="gettext('Key')"></button>
        <button class="btn conflictable conflicts-toolbar hover-adjudicator"
                data-toggle="tooltip" v-text="gettext('Constraint')"
                :title="gettext('This adjudicator or team has an unmet venue constraint.')"></button>
        <button class="btn panel-incomplete"
                data-toggle="tooltip" v-text="gettext('Incomplete')"
                :title="gettext('Debate has no venue.')"></button>
      </template>
    </drag-and-drop-actions>

    <template slot="debates">
      <drag-and-drop-debate v-for="debate in debatesOrPanels" :key="debate.id" :debateOrPanel="debate">
        <template slot="venues">fancy venues UI</template>
      </drag-and-drop-debate>
    </template>

    <template slot="modals">
      <modal-for-allocating :intro-text="gettext(allocateIntro)"
                            :context-of-action="'allocate_debate_venues'"></modal-for-allocating>
    </template>

  </drag-and-drop-layout>

</template>

<script>
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'
import ModalForAllocating from '../../utils/templates/modals/ModalForAllocating.vue'

export default {
  components: { ModalForAllocating },
  mixins: [DragAndDropContainerMixin],
  data: function () {
    return {
      highlights: {
        priority: {
          label: 'Priority',
          active: false,
          options: [],
        },
        category: {
          label: 'Category',
          active: false,
          options: [],
        },
      },
      allocateIntro: `TKTK`,
    }
  },
}
</script>
