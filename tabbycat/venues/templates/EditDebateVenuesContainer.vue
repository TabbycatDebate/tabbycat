<template>

  <drag-and-drop-layout>

    <drag-and-drop-actions slot="actions" allocate="#confirmAutoAllocationModal">
      <template slot="default-highlights">
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

  </drag-and-drop-layout>

</template>

<script>
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'

export default {
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
    }
  },
}
</script>
