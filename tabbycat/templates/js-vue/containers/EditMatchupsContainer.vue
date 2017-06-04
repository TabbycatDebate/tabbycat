<template>
  <div class="col-md-12 draw-container">

    <div class="vertical-spacing" id="messages-container"></div>

    <slide-over-item :subject="slideOverItem"></slide-over-item>

    <draw-header :positions="positions">
      <template slot="hteams">
        <div class="thead flex-cell flex-8 vue-droppable-container" data-toggle="tooltip" title="test"
          v-for="position in positions">
          <span>{{ position }}</span>
        </div>
      </template>
    </draw-header>

    <debate v-for="debate in debates" :debate="debate" :key="debate.id">
      <template v-for="(team, index) in debate.teams">
        <div class="draw-cell flex-8 vue-droppable-container" :slot="'sposition' + index">
          <droppable-generic>
            <draggable-team :team="team"></draggable-team>
          </droppable-generic>
        </div>
      </template>
    </debate>

    <unallocated-items-container>
      <div v-for="unallocatedTeam in unallocatedItems">
        <draggable-team :team="unallocatedTeam"> </draggable-team>
      </div>
    </unallocated-items-container>

  </div>
</template>

<script>
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import UnallocatedItemsContainer from '../containers/UnallocatedItemsContainer.vue'
import DrawHeader from '../draw/DrawHeader.vue'
import Debate from '../draw/Debate.vue'
import DroppableGeneric from '../draganddrops/DroppableGeneric.vue'
import DraggableTeam from '../draganddrops/DraggableTeam.vue'
import SlideOverItem from '../infoovers/SlideOverItem.vue'
import _ from 'lodash'

export default {
  mixins: [DrawContainerMixin],
  components: {
    DrawHeader, UnallocatedItemsContainer, Debate, DroppableGeneric,
    DraggableTeam, SlideOverItem
  }
}

</script>
