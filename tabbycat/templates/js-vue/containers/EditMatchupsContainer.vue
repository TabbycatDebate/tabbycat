<template>
  <div class="col-md-12 draw-container">

    <div class="row nav-pills">
      <a class="btn btn-default submit-disable" :href="backUrl">
        <span class="glyphicon glyphicon-chevron-left"></span> Back to Draw
      </a>
      <auto-save-counter :css="'btn-md pull-right'"></auto-save-counter>
    </div>

    <div class="row">
      <div class="vertical-spacing" id="messages-container"></div>
    </div>

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

    <slide-over-item :subject="slideOverItem"></slide-over-item>

  </div>
</template>

<script>
import DrawContainerMixin from '../containers/DrawContainerMixin.vue'
import DraggableTeam from '../draganddrops/DraggableTeam.vue'
import _ from 'lodash'

export default {
  mixins: [DrawContainerMixin],
  components: { DraggableTeam },
  methods: {
    moveToUnused() {
      console.log('moveTeamToUnused')
    }
  },
}

</script>
